#!/usr/bin/env python3
"""Detailed-muon crossing diagnostics and binned Landau–Gaussian fits.

Local chords between adjacent primary-muon contribution centroids approximate
incidence. They do not reconstruct Geant4 step lengths. Efficiency retains all
48 nominal opportunities per event separately from the qualified spectrum.
"""
from array import array
import json
import math
from pathlib import Path

import numpy as np


def geometry(args):
    import ROOT
    import dd4hep
    from podio import root_io
    from digitized_response import sha, write
    args.work.mkdir(parents=True,exist_ok=True)
    if (args.work/'muon-geometry.json').exists():
        raise ValueError('Geometry summary already exists; use a fresh work path')
    ROOT.DisableImplicitMT()
    ROOT.gROOT.SetBatch(True)
    if ROOT.gSystem.Load(str(args.odd_library.resolve())) < 0:
        raise RuntimeError('ODD factory load failed')
    detector=dd4hep.Detector.getInstance()
    detector.fromXML(str((args.odd_source/'xml/OpenDataDetector.xml').resolve()))
    manager=detector.manager()
    volume_manager=detector.volumeManager()
    mm=float(dd4hep.mm)
    normals={}
    reference_outside=0;maximum_reference_residual=0.;queries=0
    for sample in json.loads(args.muon_samples.read_text())['samples']:
        name='ECalBarrelCollection' if sample['eta']==0 else 'ECalEndcapCollection'
        frames=root_io.Reader(sample['path']).get('events')
        for frame in frames:
            for hit in frame.get(name):
                cid=int(hit.getCellID())
                key=f'{name}:{(cid>>11)&15}:{(cid>>8)&7}'
                point=hit.getPosition()
                # A virtual boundary-cell reference can overhang its physical
                # sensitive footprint. Resolve its actual volume by the ID,
                # rather than assigning the normal of the containing point.
                context=volume_manager.lookupContext(cid)
                volume=context.volumePlacement().volume()
                if str(volume.material().name())!='Silicon':
                    raise ValueError('Sensitive volume ID does not resolve to Silicon')
                shape=volume.solid().ptr()
                endcap=name=='ECalEndcapCollection'
                half_thickness=float(shape.GetDy1() if endcap else shape.GetDZ())/mm
                if abs(half_thickness-.25)>1e-7 or (endcap and abs(float(shape.GetDy2())/mm-.25)>1e-7):
                    raise ValueError('Unexpected sensitive half thickness')
                p0=context.localToWorld(dd4hep.Position(0,0,0))
                p1=context.localToWorld(dd4hep.Position(0,1,0) if endcap else dd4hep.Position(0,0,1))
                normal=np.array([p1.x()-p0.x(),p1.y()-p0.y(),p1.z()-p0.z()])
                normal/=np.linalg.norm(normal)
                reference=context.localToWorld(detector.readout(name).segmentation().position(cid))
                residual=max(abs(reference.x()/mm-point.x),abs(reference.y()/mm-point.y),abs(reference.z()/mm-point.z))
                maximum_reference_residual=max(maximum_reference_residual,residual)
                if residual>.002:
                    raise ValueError('Stored reference disagrees with native segmentation/volume transform')
                node=manager.FindNode(point.x*mm,point.y*mm,point.z*mm)
                reference_outside+=int(not node or str(node.GetVolume().GetMaterial().GetName())!='Silicon')
                queries+=1
                if key in normals and np.linalg.norm(np.asarray(normals[key])-normal)>1e-9:
                    raise ValueError('Nonuniform module normal')
                normals[key]=list(normal)
    result=dict(normals=normals,silicon_thickness_mm=.5,
                cell_reference_queries=queries,virtual_references_outside_silicon=reference_outside,
                maximum_cell_reference_residual_mm=maximum_reference_residual,position_tolerance_mm=.002,
                odd_library_sha256=sha(args.odd_library),
                odd_xml_sha256=sha(args.odd_source/'xml/detectors/CalorimeterECal.xml'),
                muon_manifest_sha256=sha(args.muon_samples),
                source_sha256=sha(Path(__file__)),
                input_sha256=[s['sha256'] for s in json.loads(args.muon_samples.read_text())['samples']],
                query='DD4hep VolumeManager sensitive-volume lookup by cellID; Silicon barrel box DZ=0.25mm, endcap trapezoid Dy1=Dy2=0.25mm; local-z/barrel or local-y/endcap normal transformed to world; all references checked against native segmentation',
                limitations=['All persisted cell centres in these two detailed-muon samples were queried; this does not map unhit channels or transported zero-deposit crossings.'])
    write(args.work/'muon-geometry.json',result)
    dd4hep.Detector.destroyInstance()
    print('Muon native geometry normals verified',len(normals))


def fit_landau_gaussian(hist, label, full=True):
    import ROOT
    ROOT.gROOT.SetBatch(True)
    if not hasattr(ROOT,'nodd_validation_langau'):
        ROOT.gInterpreter.Declare(r'''
#include <TMath.h>
double nodd_validation_langau(double* x, double* p) {
  // Normalized Gaussian convolution of a normalized Landau distribution.
  // ROOT's unit-Landau mode is -0.22278298; p[1] is its unbroadened MPV.
  double value=0.;
  const int n=80;
  const double step=10.*p[3]/n;
  for(int i=0;i<n;++i) {
    double delta=-5.*p[3]+(i+.5)*step;
    value+=TMath::Landau(x[0]-delta,p[1]+.22278298*p[2],p[2],true)
          *TMath::Gaus(delta,0.,p[3],true)*step;
  }
  return p[0]*value;
}
''')
    edges=array('d',hist['edges'])
    h=ROOT.TH1D('mip_'+label,'',len(edges)-1,edges)
    h.SetDirectory(0)
    for i,n in enumerate(hist['counts']):
        h.SetBinContent(i+1,n)
        h.SetBinError(i+1,math.sqrt(n))
    width=edges[1]-edges[0]
    f=ROOT.TF1('langau_'+label,ROOT.nodd_validation_langau,.25,2.5,4)
    f.SetParNames('area_binwidth','Landau_MPV','Landau_width','Gaussian_sigma')
    f.SetParameters(sum(hist['counts'])*width,1.,.07,.10)
    f.SetParLimits(0,1.,100000.)
    f.SetParLimits(1,.6,1.4)
    f.SetParLimits(2,.01,.3)
    f.SetParLimits(3,.002,.4)
    result=h.Fit(f,'LQNS0I','',.25,2.5)
    status=int(result)
    if status or result.CovMatrixStatus()<2:
        raise RuntimeError(f'LandauGaussian fit failed ({label}): {status}, covariance {result.CovMatrixStatus()}')
    if not full:
        return dict(underlying_Landau_MPV=float(f.GetParameter(1)),convolved_peak=float(f.GetMaximumX(.25,2.5)))
    xs=np.linspace(.25,2.5,451)
    observed=np.asarray(hist['counts'][10:100],dtype=float)
    expected=np.array([float(f.Integral(edges[i],edges[i+1])/width) for i in range(10,100)])
    positive=observed>0
    deviance=2*float(np.sum(expected-observed)+np.sum(observed[positive]*np.log(observed[positive]/expected[positive])))
    p_value=float(ROOT.TMath.Prob(deviance,int(f.GetNDF())))
    bounds=[(1.,100000.),(.6,1.4),(.01,.3),(.002,.4)]
    boundary=[i for i,(low,high) in enumerate(bounds) if min(f.GetParameter(i)-low,high-f.GetParameter(i))<1e-4*(high-low)]
    flags=[]
    if boundary:flags.append('parameter_near_fit_limit')
    if p_value<.001:flags.append('asymptotic_deviance_p_below_0.001')
    return dict(model='Normalized Landau convolved with Gaussian; binned Poisson likelihood',
                fit_range_MIP=[.25,2.5],bin_width_MIP=width,
                range_expected_entries=float(f.Integral(.25,2.5)/width),
                likelihood_normalization='Bin-integrated Poisson means; free total-area coefficient profiles normalization over the finite fitted range',
                parameter_names=['area_times_binwidth','Landau_MPV','Landau_width','Gaussian_sigma'],
                parameters=[float(f.GetParameter(i)) for i in range(4)],
                parameter_bounds=[list(v) for v in bounds],
                boundary_parameter_indices=boundary,model_diagnostic_flags=flags,
                disposition='conditional model characterization with diagnostic flags' if flags else 'conditional model characterization; optimizer converged',
                parameter_errors=[float(f.GetParError(i)) for i in range(4)],
                covariance=[[float(result.CovMatrix(i,j)) for j in range(4)] for i in range(4)],
                underlying_Landau_MPV=float(f.GetParameter(1)),MPV_fit_SE=float(f.GetParError(1)),
                convolved_peak=float(f.GetMaximumX(.25,2.5)),
                fit_status=status,covariance_status=int(result.CovMatrixStatus()),
                deviance=deviance,ndf=int(f.GetNDF()),
                asymptotic_deviance_p_value=p_value,
                goodness_of_fit_caveat='Asymptotic Poisson deviance diagnostic; correlated cells violate independent-bin sampling. Interpret with event-cluster uncertainties and residual shape.',
                curve_x_MIP=xs.tolist(),curve_counts_per_bin=[float(f.Eval(float(x))) for x in xs],
                uncertainty='Marginal fit covariance only; separate event-cluster bootstrap MPV supplied in summary. No path/material/fit-model systematic included.')


def wilson(k,n):
    z=1.959963984540054
    p=np.asarray(k)/n
    denominator=1+z*z/n
    center=(p+z*z/(2*n))/denominator
    half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/denominator
    return np.maximum(0,center-half),np.minimum(1,center+half)


def muon_summary(rows,args,pedestal):
    from podio import root_io
    from digitized_response import basic,histogram,read_events,sha
    geometry_data=json.loads((args.work/'muon-geometry.json').read_text())
    manifest=json.loads(args.muon_samples.read_text())
    if geometry_data['muon_manifest_sha256']!=sha(args.muon_samples) or geometry_data['input_sha256']!=[s['sha256'] for s in manifest['samples']] or geometry_data['odd_library_sha256']!=manifest['odd_library_sha256']:
        raise ValueError('Geometry summary does not match executed muon input/factory identity')
    output=[]
    thresholds=np.array([0,.2,.4,.6,.8,1.,1.2,1.5,2.])
    mip=json.loads(args.mip_calibration.read_text())['mip_energy_GeV']
    for row in rows:
        if row['kind']!='muons':
            continue
        eta=row['sample']['eta']
        collection='ECalBarrelCollection' if eta==0 else 'ECalEndcapCollection'
        frames=root_io.Reader(row['sample']['path']).get('events')
        diagnostics=read_events(row)
        if len(frames)!=len(diagnostics):
            raise ValueError('Muon frame count mismatch')
        values={stage:[] for stage in ['raw','off','on']}
        selected_values={stage:[] for stage in ['off','on']}
        # Fit histograms are also retained by event locally for cluster resampling.
        event_values={stage:[] for stage in values}
        efficiency_counts=[]
        single_counts=[];split_counts=[];single_denominators=[];split_denominators=[]
        raw_paths=[]; chord_cosines=[]; path_ratio=[]
        counters=dict(nominal_layer_opportunities=48*len(frames),missing_primary_layer=0,
                      split_primary_layer=0,contaminated_single_cell_layer=0,
                      qualified_spectrum_crossings=0,chord_unavailable=0,incidence_rejected=0,
                      detailed_muon_contributions=0,non_muon_contributions=0)
        for index,(frame,event) in enumerate(zip(frames,diagnostics)):
            headers=frame.get('EventHeader')
            if len(headers)!=1 or [int(headers[0].getRunNumber()),int(headers[0].getEventNumber())]!=event['identity']:
                raise ValueError('Muon EventHeader mismatch')
            particles=[p for p in frame.get('MCParticles') if p.getGeneratorStatus()==1]
            if len(particles)!=1 or particles[0].getPDG()!=13:
                raise ValueError('Expected single primary muon')
            primary=particles[0]
            primary_oid=(int(primary.getObjectID().collectionID),int(primary.getObjectID().index))
            momentum=primary.getMomentum()
            truth=np.array([momentum.x,momentum.y,momentum.z],float)
            truth/=np.linalg.norm(truth)
            signed={mode:{int(cid):value for cid,value in event['modes'][mode]['cells'][collection]}
                    for mode in ['off','on']}
            primary_layers={layer:[] for layer in range(1,49)}
            centers={}
            for hit in frame.get(collection):
                cid=int(hit.getCellID()); layer=(cid>>16)&63
                muon_cs=[]
                for c in hit.getContributions():
                    if int(c.getPDG())==13:
                        counters['detailed_muon_contributions']+=1
                    else:
                        counters['non_muon_contributions']+=1
                    particle=c.getParticle()
                    if int(c.getPDG())==13 and particle.isAvailable() and (int(particle.getObjectID().collectionID),int(particle.getObjectID().index))==primary_oid:
                        muon_cs.append(c)
                if muon_cs:
                    if layer not in primary_layers:
                        raise ValueError('Invalid primary layer')
                    primary_layers[layer].append((hit,muon_cs))
            counts=np.zeros((2,len(thresholds)),dtype=int)
            category_counts=[np.zeros_like(counts),np.zeros_like(counts)]
            category_denominators=[0,0]
            for layer,hits in primary_layers.items():
                if not hits:
                    counters['missing_primary_layer']+=1
                    continue
                if len(hits)>1:
                    counters['split_primary_layer']+=1
                category=int(len(hits)>1)
                category_denominators[category]+=1
                for j,mode in enumerate(['off','on']):
                    maximum=max(signed[mode][int(h.getCellID())] for h,_ in hits)
                    passes=maximum>thresholds.astype(np.float32)
                    counts[j]+=passes
                    category_counts[category][j]+=passes
                positions=[]; weights=[]
                for _,cs in hits:
                    for c in cs:
                        p=c.getStepPosition()
                        positions.append([p.x,p.y,p.z]);weights.append(c.getEnergy())
                centers[layer]=np.average(positions,axis=0,weights=weights)
            efficiency_counts.append(counts)
            single_counts.append(category_counts[0]);split_counts.append(category_counts[1])
            single_denominators.append(category_denominators[0]);split_denominators.append(category_denominators[1])
            current={stage:[] for stage in values}
            for layer,hits in primary_layers.items():
                if len(hits)!=1:
                    continue
                hit,cs=hits[0]
                # No deposit-based cut: require known muon provenance only.
                if len(cs)!=len(hit.getContributions()):
                    counters['contaminated_single_cell_layer']+=1
                    continue
                if layer-1 not in centers or layer+1 not in centers:
                    counters['chord_unavailable']+=1
                    continue
                chord=centers[layer+1]-centers[layer-1]
                norm=np.linalg.norm(chord)
                if not norm>0:
                    raise ValueError('Zero local chord')
                chord/=norm
                cid=int(hit.getCellID())
                key=f'{collection}:{(cid>>11)&15}:{(cid>>8)&7}'
                if key not in geometry_data['normals']:
                    raise ValueError('Unverified sensitive module normal')
                normal=np.asarray(geometry_data['normals'][key])
                cosine=abs(float(chord@normal))
                straight=abs(float(truth@normal))
                if cosine<.9:
                    # Fixed near-normal category; retained efficiency denominator.
                    counters['incidence_rejected']+=1
                    continue
                chord_cosines.append(cosine)
                raw_paths.append(.5/cosine)
                path_ratio.append(straight/cosine)
                counters['qualified_spectrum_crossings']+=1
                for stage,val in [('raw',float(hit.getEnergy())/mip),('off',signed['off'][cid]),('on',signed['on'][cid])]:
                    current[stage].append(val*cosine)
                    values[stage].append(val*cosine)
                    if stage in selected_values and val>np.float32(.6):
                        selected_values[stage].append(val*cosine)
            for stage in values:
                event_values[stage].append(current[stage])
        if not counters['detailed_muon_contributions'] or not len(raw_paths):
            raise ValueError('Detailed primary contribution/path evidence absent')
        count_array=np.asarray(efficiency_counts)
        rng=np.random.Generator(np.random.PCG64(119403))
        indices=rng.integers(0,len(frames),(1000,len(frames)))
        joint=count_array[indices].sum(axis=1)/(48*len(frames))
        totals=count_array.sum(axis=0)
        efficiencies={}
        for j,mode in enumerate(['off','on']):
            low,high=wilson(totals[j],48*len(frames))
            efficiencies[mode]=dict(accepted_counts=totals[j].tolist(),denominator=48*len(frames),
                efficiency=(totals[j]/(48*len(frames))).tolist(),
                event_cluster_bootstrap_SE=joint[:,j].std(axis=0,ddof=1).tolist(),
                event_cluster_bootstrap_CI95=np.quantile(joint[:,j],[.025,.975],axis=0).tolist(),
                nominal_opportunity_Wilson95=[low.tolist(),high.tolist()])
        categories={}
        for name,counts,denominators in [('identified_single',single_counts,single_denominators),
                                        ('identified_split',split_counts,split_denominators)]:
            denominators=np.asarray(denominators)
            denominator=int(denominators.sum())
            if not denominator:
                categories[name]=dict(denominator=0,efficiency=None)
                continue
            counts=np.asarray(counts)
            total=counts.sum(axis=0)
            resampled_denominator=denominators[indices].sum(axis=1)
            category_joint=np.full((1000,2,len(thresholds)),np.nan)
            np.divide(counts[indices].sum(axis=1),resampled_denominator[:,None,None],
                      out=category_joint,where=resampled_denominator[:,None,None]>0)
            undefined=int(np.sum(resampled_denominator==0))
            low,high=wilson(total,denominator)
            categories[name]=dict(denominator=denominator,
                accepted_counts=total.tolist(),efficiency=(total/denominator).tolist(),
                conditional_crossing_Wilson95=[low.tolist(),high.tolist()],
                event_cluster_bootstrap_undefined_replicates=undefined,
                event_cluster_bootstrap_SE=None if undefined else category_joint.std(axis=0,ddof=1).tolist(),
                event_cluster_bootstrap_CI95=None if undefined else np.quantile(category_joint,[.025,.975],axis=0).tolist())
        spectra={}
        for stage in values:
            h=histogram(values[stage],np.linspace(0,5,201),'MIP at 0.5 mm equivalent path')
            fit=fit_landau_gaussian(h,f'eta{eta}_{stage}')
            # The fit covariance ignores within-event layer dependence. Refit a
            # fixed 1000 whole-event resamples with identical binning and range.
            counts_by_event=np.array([np.histogram(v,bins=np.asarray(h['edges']))[0] for v in event_values[stage]])
            fit_rng=np.random.Generator(np.random.PCG64(119401))
            boot=[]; peaks=[]; failed=0
            for b in range(1000):
                bh=dict(h,counts=counts_by_event[fit_rng.integers(0,len(frames),len(frames))].sum(axis=0).tolist())
                try:
                    bf=fit_landau_gaussian(bh,f'eta{eta}_{stage}_b{b}',full=False)
                    boot.append(bf['underlying_Landau_MPV'])
                    peaks.append(bf['convolved_peak'])
                except RuntimeError:
                    failed+=1
            if failed>50:
                raise RuntimeError(f'MIP bootstrap has {failed} undefined fits (>5%); no interval quoted')
            fit['bootstrap_failed_fits']=failed
            fit['MPV_event_cluster_bootstrap_SE']=float(np.std(boot,ddof=1))
            fit['MPV_event_cluster_bootstrap_CI95']=np.quantile(boot,[.025,.975]).tolist()
            fit['bootstrap_replications']=len(boot)
            fit['convolved_peak_event_cluster_bootstrap_SE']=float(np.std(peaks,ddof=1))
            fit['convolved_peak_event_cluster_bootstrap_CI95']=np.quantile(peaks,[.025,.975]).tolist()
            spectra[stage]=dict(histogram=h,fit=fit,
                empirical_mode_MIP=float((np.asarray(h['edges'][:-1])+np.asarray(h['edges'][1:]))[int(np.argmax(h['counts']))]/2),
                empirical_quantiles_MIP=np.quantile(values[stage],[.1,.25,.5,.75,.9]).tolist())
            # Threshold is applied in actual pulse units before path correction.
            # Persist the separate selected-output histogram to avoid presenting
            # a prethreshold model prediction as a measured digitized spectrum.
            if stage in selected_values:
                spectra[stage]['actual_thresholded_output']=histogram(selected_values[stage],np.linspace(0,5,201),'MIP at 0.5 mm equivalent path')
        signal=spectra['on']['fit']['underlying_Landau_MPV']
        signal_SE=spectra['on']['fit']['MPV_event_cluster_bootstrap_SE']
        noise=pedestal['SD'];noise_SE=noise/math.sqrt(2*(pedestal['n']-1))
        output.append(dict(eta=eta,events=len(frames),counters=counters,
            path_mm=basic(raw_paths),cosine=basic(chord_cosines),straight_over_chord_path=basic(path_ratio),
            spectra=spectra,thresholds_MIP=thresholds.tolist(),efficiency=efficiencies,
            identified_crossing_categories=categories,
            efficiency_joint_covariance=np.cov(joint.reshape(1000,-1).T,ddof=1).tolist(),
            efficiency_joint_order='off thresholds ascending, then on thresholds ascending',
            SNR=dict(signal_MIP=signal,signal_SE=signal_SE,noise_RMS_MIP=noise,noise_RMS_SE=noise_SE,
                     ratio=signal/noise,ratio_SE=math.sqrt((signal_SE/noise)**2+(signal*noise_SE/noise**2)**2),
                     convention='Fitted path-normalized underlying Landau MPV divided by signed empty-channel pedestal RMS in MIP; comparator study setting, not detector noise qualification'),
            limitations=['Path normalization uses adjacent-layer muon contribution centroids and native slab normal; no Geant4 step-length reconstruction.',
                         'MIP spectrum requires one pure-primary-muon cell, adjacent layer centroids and incidence cosine >=0.9; endpoints/split/contaminated layers excluded from spectrum only.',
                         'Efficiency counts any primary-associated cell above threshold per nominal layer; all 48 layers/event, including missing and split layers. Missing truth is separately counted and is not certified zero deposit.',
                         'Thresholds are applied to unnormalized channel MIPs. No empty-channel false-hit field is added to sparse simulation hits.']))
    return dict(samples=output,geometry=geometry_data,geometry_summary_sha256=sha(args.work/'muon-geometry.json'))
