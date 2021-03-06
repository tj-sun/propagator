from sympy import factorial, symbols, Indexed, IndexedBase, solve, Matrix, Rational, Eq, simplify
from sympy.printing.ccode import CCodePrinter
from matplotlib import animation
import numpy as np
import matplotlib.pyplot as plt

shift_t = ['Txx','Tyy','Txy']
shift_x = ['U','Txy']
shift_y = ['V','Txy']
hf = Rational(1,2) # 1/2

class MyCPrinter(CCodePrinter):
	def __init__(self, settings={}):
		CCodePrinter.__init__(self, settings)

	def _print_Indexed(self, expr):
		# Array base and append indices
		output = self._print(expr.base.label) + ''.join(['[' + self._print(x) + ']' for x in expr.indices])
		return output

	def _print_Rational(self, expr):
		p, q = int(expr.p), int(expr.q)
		return '%d.0F/%d.0F' % (p, q) # float precision by default

class MyPochoirPrinter(CCodePrinter):
	def __init__(self, settings={}):
		CCodePrinter.__init__(self, settings)

	def _print_Indexed(self, expr):
		# Array base and append indices
		output = self._print(expr.base.label) + '(' + ','.join(self._print(x) for x in expr.indices) + ')'
		return output

	def _print_Rational(self, expr):
		p, q = int(expr.p), int(expr.q)
		return '%d.0/%d.0' % (p, q) # float precision by default

def tc(dx, n):
    # return coefficient of power n Taylor series term
    return (dx**n)/factorial(n)

def Taylor(dx, n):
    # return Matrix of Taylor Coefficients M, such that M * D = R
    # where D is list of derivatives at x [f, f', f'' ..]
    # R is value at neighbour grid point [.. f(x-dx), f(x), f(x+dx) ..]
    l = []
    for i in range(-n+1,n):
    	ll = [tc((i*dx),j) for j in range(2*n-1)]
    	l.append(ll)
    return Matrix(l)

def Taylor_half(dx, n):
    # return Matrix of Taylor Coefficients M, such that M * D = R
    # where D is list of derivatives at x [f, f', f'' ..]
    # R is value at neighbour grid point [.. f(x-dx/2), f(x), f(x+dx/2), f(x+3/2*dx) ..]
    l = []
    for i in range(-n*2+1,n*2,2):
    	ll = [tc((i*dx/2),j) for j in range(2*n)]
    	l.append(ll)
    return Matrix(l)

def Deriv(U, i, k, d, n):
	# get the FD approximation for nth derivative in terms of grid U
	# i is list of indices of U, e.g. [x,y,z,t] for 3D
	# k = which dimension to expand, k=0 for x, k=1 for t etc
	M = Taylor(d, n)
	s = [0]*len(i)
	s[k] = 1 # switch on kth dimension
	# generate matrix of RHS, i.e. [ ... U[x-1], U[x], U[x+1] ... ]
	if len(i)==1:
		RX = Matrix([U[i[0]+s[0]*x] for x in range(-n+1,n)])
	elif len(i)==2:
		RX = Matrix([U[i[0]+s[0]*x,i[1]+s[1]*x] for x in range(-n+1,n)])
	elif len(i)==3:
		RX = Matrix([U[i[0]+s[0]*x,i[1]+s[1]*x,i[2]+s[2]*x] for x in range(-n+1,n)])
	elif len(i)==4:
		RX = Matrix([U[i[0]+s[0]*x,i[1]+s[1]*x,i[2]+s[2]*x,i[3]+s[3]*x] for x in range(-n+1,n)])
	else:
		raise NotImplementedError(">4 dimensions, need to fix")

	return M.inv() * RX

def Deriv_half(U, i, k, d, n, shift_forward=True):
	# get the FD approximation for nth derivative in terms of grid U
	# i is list of indices of U, e.g. [x,y,z,t] for 3D
	# k = which dimension to expand, k=0 for x, k=1 for t etc
	M = Taylor_half(d, n)
	s = [0]*len(i)
	s[k] = 1 # switch on kth dimension
	# generate matrix of RHS, i.e. [ ... U[x-1], U[x], U[x+1] ... ]
	if len(i)==1:
		RX = Matrix([U[i[0]+s[0]*x*hf] for x in range(-n*2+1,n*2,2)])
	elif len(i)==2:
		RX = Matrix([U[i[0]+s[0]*x*hf,i[1]+s[1]*x*hf] for x in range(-n*2+1,n*2,2)])
	elif len(i)==3:
		RX = Matrix([U[i[0]+s[0]*x*hf,i[1]+s[1]*x*hf,i[2]+s[2]*x*hf] for x in range(-n*2+1,n*2,2)])
	elif len(i)==4:
		RX = Matrix([U[i[0]+s[0]*x*hf,i[1]+s[1]*x*hf,i[2]+s[2]*x*hf,i[3]+s[3]*x*hf] for x in range(-n*2+1,n*2,2)])
	else:
		raise NotImplementedError(">4 dimensions, need to fix")

	result = M.inv() * RX
	if shift_forward:
		return result.subs(i[k],i[k]+hf)
	else:
		return result.subs(i[k],i[k]-hf)

def Deriv_half_2(U, i, k, d, n):
	# get the FD approximation for nth derivative in terms of grid U
	# i is list of indices of U, e.g. [x,y,z,t] for 3D
	# k = which dimension to expand, k=0 for x, k=1 for t etc
	M = Taylor_half(d, n)
	s = [0]*len(i)
	s[k] = 1 # switch on kth dimension
	# generate matrix of RHS, i.e. [ ... U[x-1], U[x], U[x+1] ... ]
	if len(i)==1:
		RX = Matrix([U[i[0]+s[0]*x*hf] for x in range(-n*2+1,n*2,2)])
	elif len(i)==2:
		RX = Matrix([U[i[0]+s[0]*x*hf,i[1]+s[1]*x*hf] for x in range(-n*2+1,n*2,2)])
	elif len(i)==3:
		RX = Matrix([U[i[0]+s[0]*x*hf,i[1]+s[1]*x*hf,i[2]+s[2]*x*hf] for x in range(-n*2+1,n*2,2)])
	elif len(i)==4:
		RX = Matrix([U[i[0]+s[0]*x*hf,i[1]+s[1]*x*hf,i[2]+s[2]*x*hf,i[3]+s[3]*x*hf] for x in range(-n*2+1,n*2,2)])
	else:
		raise NotImplementedError(">4 dimensions, need to fix")

	result = M.inv() * RX
	return result

def shift_grid(expr):
	if expr.is_Symbol:
		return expr
	if expr.is_Number:
		return expr
	if isinstance(expr,Indexed):
		b = expr.base
		idx = list(expr.indices)
		if b.label.name in shift_x:
			idx[1] -= hf
		if b.label.name in shift_y:
			idx[2] -= hf
		t = Indexed(b,*idx)
		return t
	args = tuple([shift_grid(arg) for arg in expr.args])
	expr2 = expr.func(*args)
	return expr2

def print_myccode(expr, assign_to=None, pochoir=False, **settings):
	if pochoir:
		return MyPochoirPrinter(settings).doprint(expr, assign_to)
	else:
		return MyCPrinter(settings).doprint(expr, assign_to)

def print_assignment(eq, s, s0=0, pochoir=False):
	s1 = print_myccode(s, None, pochoir)
	if(s0==0):
		s2 = print_myccode(simplify(solve(eq,s)[0]), None, pochoir)
	else:
		s2 = print_myccode(simplify(solve(eq,s)[0] - s0) + s0, None, pochoir)
	return s1 + '=' + s2

# def print_increment(eq, s, s0):
# 	# express s as increment of s0, and drop the index
# 	s1 = print_myccode(drop_time(s))
# 	s2 = print_myccode(drop_time(simplify(solve(eq,s)[0] - s0)))
# 	return s1 + '+=' + s2

# def drop_time(expr):
# 	# a bit ugly implementation
# 	s = srepr(expr);
# 	s = s.replace(", Symbol('t')","")
# 	s = s.replace(", Add(Symbol('t'), Integer(1))","")
# 	return eval(s)

def IndexedBases(s):
	l = s.split();
	bases = [IndexedBase(x) for x in l]
	return tuple(bases)

def advance_time(expr,d):
	return Eq(expr.lhs, expr.rhs.xreplace(d))

def assign_pochoir_bc(expr):
	return "return " + print_myccode(expr,pochoir=True);

def main():
	dx, dt, x, y, z, t, c = symbols('dx dt x y z t c')
	U = IndexedBase('U')
	n = 2
	Uxx = Deriv(U,[x,y,z,t],0,dx,n)[2]
	Utt = Deriv(U,[x,y,z,t],3,dt,n)[2]
	eq = Eq(Utt, (c**2)*Uxx)
	code = print_myccode(U[x,y,z,t+1]) + "=" + print_myccode(solve(eq, U[x,y,z,t+1])[0])
	print(code)

if __name__ == "__main__":
    main()