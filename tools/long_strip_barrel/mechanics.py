"""Independent linear Timoshenko mesh, block-tridiagonal solve (standard library).
Two DOFs per node: transverse deflection and rotation. All bearing displacements
fixed; rotations free. Actual point masses and a uniform continuous mass load.
"""
import math

def inv(a):
 d=a[0][0]*a[1][1]-a[0][1]*a[1][0]
 if d<=0:raise ValueError('Nonpositive beam stiffness')
 return [[a[1][1]/d,-a[0][1]/d],[-a[1][0]/d,a[0][0]/d]]
def mm(a,b):return [[sum(a[i][k]*b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
def mv(a,b):return [sum(a[i][j]*b[j] for j in range(2)) for i in range(2)]
def transpose(a):return [list(x) for x in zip(*a)]
def solve(c,payload,screen,mesh_mm=20):
 H=c['half_length_mm'];anchors=screen['anchors_z_mm'];fixed=set(anchors);points=payload['point_loads'];knots=sorted(set([-H,H]+anchors+[z for z,m in points]))
 nodes=[knots[0]]
 for a,b in zip(knots,knots[1:]):
  n=max(1,math.ceil((b-a)/mesh_mm));nodes.extend(a+(b-a)*j/n for j in range(1,n));nodes.append(b)
 nodes=sorted(set(nodes));A=[[[0.,0.],[0.,0.]] for z in nodes];B=[[[0.,0.],[0.,0.]] for z in nodes[:-1]];F=[[0.,0.] for z in nodes];q=payload['continuous_g']/1000*9.80665/(2*H)*screen['load_factor'];EI=screen['EI_N_mm2'];S=screen['shear_rigidity_N']
 for i,(a,b) in enumerate(zip(nodes,nodes[1:])):
  L=b-a;ph=12*EI/(S*L*L);v=EI/(L**3*(1+ph));K=[[12,6*L,-12,6*L],[6*L,(4+ph)*L*L,-6*L,(2-ph)*L*L],[-12,-6*L,12,-6*L],[6*L,(2-ph)*L*L,-6*L,(4+ph)*L*L]]
  for row in range(2):
   for col in range(2):A[i][row][col]+=v*K[row][col];A[i+1][row][col]+=v*K[row+2][col+2];B[i][row][col]=v*K[row][col+2]
  F[i][0]+=q*L/2;F[i+1][0]+=q*L/2;F[i][1]+=q*L*L/12;F[i+1][1]-=q*L*L/12
 index={z:i for i,z in enumerate(nodes)}
 for z,m in points:F[index[z]][0]+=m/1000*9.80665*screen['load_factor']
 for z in anchors:
  i=index[z];A[i][0]=[1,0];A[i][1][0]=0;F[i][0]=0
  if i>0:B[i-1][0][0]=B[i-1][1][0]=0
  if i<len(B):B[i][0]=[0,0]
 D=[A[0]];Y=[F[0]]
 for i in range(1,len(nodes)):
  C=mm(transpose(B[i-1]),inv(D[-1]));CA=mm(C,B[i-1]);CF=mv(C,Y[-1]);D.append([[A[i][r][k]-CA[r][k] for k in range(2)] for r in range(2)]);Y.append([F[i][r]-CF[r] for r in range(2)])
 X=[None]*len(nodes);X[-1]=mv(inv(D[-1]),Y[-1])
 for i in range(len(nodes)-2,-1,-1):BX=mv(B[i],X[i+1]);X[i]=mv(inv(D[i]),[Y[i][r]-BX[r] for r in range(2)])
 j=max(range(len(nodes)),key=lambda j:abs(X[j][0]));return dict(maximum_deflection_mm=abs(X[j][0]),at_z_mm=nodes[j],mesh_max_mm=mesh_mm,nodes=len(nodes),maximum_support_residual_mm=max(abs(X[index[z]][0]) for z in anchors),hypothesis='Continuous linear Timoshenko beam; free bearing rotations; no joint/torsion/thermal/dynamics qualification')
