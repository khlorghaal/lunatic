import os.path
'''
raster monospaced font

eliminates the bulky metadata of normal font formats
and allows editing fonts with any text manipulator
does not require any over-specified and opaque GUI

made to export to bdf
currently no font renderers support rmf directly



each glyph is simply a line with the character,
followed by a plaintext raster of the character
any character may be used for solid color
'.' and ' ' are transparent

the width and heigh of the glyphs is specified only once
all rasters must conform to these dimensions

character names and codepoints are omitted entirely
as the characters encoded in the file can be used
to retrieve this data from specifications

header is very assertive/strict/aggressive,
must be in the exact format

RMF
W int
H int
AUTHOR str
LICENSE str
COMMENT str
_

example

RMF
W 7
H 7
AUTHOR khlorghaal
LICENSE WTFPL
COMMENT special characters full width, alphabetical w-1, lowercase w-1 h-1, numerical w-2, bracket interior padded
_

underscore required as last line of header
strings may be empty

font name is inferred from file name
'''
TODO= None#fixme wtf does this mean

from dataclasses import dataclass as dcls
@dcls
class glyph:
	names:list[str]#optional
	#one of char or name must be
	raster:tuple#((0|1),...)
	def print(self):
		for l in self.raster:
			print(''.join(map(str,l)))
		print()
class font:
	def __init__(self, char_wh):
		self.wh= char_wh
		assert(0<self.wh[1]<2048)
		assert(0<self.wh[0]<2048)
		self.glyphs={}

	#append glyphs into font, with empty rasters
	def init_empty(glyphs):
		for k in glyphs:
			g= glyphs[k]
			present= [g.char==g_.char for g_ in self.glyphs].contains(True)
			#^ meh?
			if present:
				print('glyph \'{}\' already present',g)
			else:
				TODO

	def print_chars(self,space=False):
		a= ''
		for (ch,g) in self.glyphs.items():
			a+= ch+(' ' if space else '')
		print(a)

	def save(self,fname):
		validate()
		TODO

	#gen_variants will generate [bold, italic][1x,2x,3x,4x]
	def save_bdf(self,fname,gen_variants=False):
		import bdflib
		from bdflib import model
		from bdflib import writer
		self.validate()
		name= os.path.splitext(fname)[0].encode('utf-8')
		bdf= bdflib.model.Font(name,1,700,800)
		for (ch,g) in self.glyphs.items():
			#bdflib *must* take an array of string-ints
			#because god is a lie
			rast= g.raster[::-1]#y axis flip
			#this trash converts the raster into
			rast= [ ['1' if c=='x' else '0' for c in r] for r in rast]
			#chars of 0|1
			rast= [ ''.join(r) for r in rast]
			#merge the chars into a line
			rast= [ int(r,2)*2 for r in rast] #*2 because ??????
			#each line is string-parsed radix2 into int
			rast= [ b'%02x'%r for r in rast]
			#then converted back to a hex string
			bdf.new_glyph_from_data(
				name= bytes(ch,'utf-8'),
				data= rast,
				bbX=-3,
				bbY=0,
				bbW=self.wh[0],
				bbH=self.wh[1],
				advance= 0,
				codepoint= ord(ch))
		bdflib.writer.write_bdf(bdf, open(fname,'wb'))




def load(fname):
	with open(fname,'r') as f:
		lines= f.read().split('\n')

		#header, aggro
		assert(lines[0]=='RMF')
		w= int(lines[1][2:])
		h= int(lines[2][2:])
		assert(lines[6]=='__')
		begin= 8-1#line of first glyph

		f= font((w,h))

		for i,l in enumerate(lines[begin:]):
			if i%(w+1)!=0:
				ll=len(l)
				if ll!=w:
					print('L:%s raster line miswidthed ==%i =%i %s'%(i+begin+1,w,ll,l))


		stride= h+1 #raster h + char identifier
		line_num=begin
		while line_num<len(lines):
			ln= line_num+1 # +1 because evil 1-indexing on files
			def warn(s):
				print('warn: glyph: L:{:<5} {}'.format(ln,s))
			datum= lines[line_num:line_num+stride]
			
			if 0\
				or len(datum[0])==0\
				or datum[0]==' '\
				or datum[0]=='\n'\
				or datum[0][:2]=='//':#comments
					line_num+=1
					continue

			names= datum[0].strip().split(' ')
			assert(len(names )!=0)
			for n in names:
				if len(n)==0:
					warn('malf gnames')
			tll= None

			#these both will replace the first

			rast= datum[1::]
			lr= len(rast) #FIXME misalignment check
			if len(rast)!=h:
				warn('malf raster != height\n%s'%rast)
			for l in rast:
				ll= len(l)
				if(ll!=w):
					warn('malf raster != width \n%s'%l)

			#L= lambda c: ' ' if c=='.' or c==' ' else 'x'
			L= lambda c: 0 if c in '.   0_' else 1
			rast= [[L(c) for c in l] for l in rast]
			rast= rast[::-1]#y axis flip
			rast= tuple(tuple(l) for l in rast)

			assert(len(names)>0)
			g= glyph(names,rast)
			for n in names:
				if f.glyphs.get(n)!=None:
					warn('name is already assigned, replacing')
				f.glyphs[n]= g

			line_num+= stride

		#special case because token delim
		if 'space' in f.glyphs:
			f.glyphs['space'].names+=[' ']

		return f

