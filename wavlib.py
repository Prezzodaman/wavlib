import random

class Wave:
	def open(self,filename):
		with open(filename,"rb") as file:
			if file.read(4)==b"RIFF":
				file.seek(22)
				self.channels=int.from_bytes(file.read(2),byteorder="little")
				self.sample_rate=int.from_bytes(file.read(4),byteorder="little")
				file.seek(34)
				self.bit_depth=int.from_bytes(file.read(2),byteorder="little")
				file.seek(40)
				self.data_length=int.from_bytes(file.read(4),byteorder="little")
				wav_bytes=[]
				while file.tell()<self.data_length+44:
					if self.channels==1:
						if self.bit_depth==8: # mono 8-bit
							byte=file.read(1)[0]
							wav_bytes.append((byte<<8)-32768)
						elif self.bit_depth==16: # mono 16-bit
							byte=file.read(2)
							byte_temp=byte[0] | (byte[1]<<8)
							byte=((byte_temp+32768) & 65535)-32768
							wav_bytes.append(byte)
					elif self.channels==2:
						if self.bit_depth==8: # stereo 8-bit
							byte=file.read(2)
							wav_bytes.append([(byte[0]<<8)-32768,(byte[1]<<8)-32768])
						elif self.bit_depth==16: # stereo 16-bit
							byte=file.read(4)
							left_temp=byte[0] | (byte[1]<<8)
							right_temp=byte[2] | (byte[3]<<8)
							left=((left_temp+32768) & 65535)-32768
							right=((right_temp+32768) & 65535)-32768
							wav_bytes.append([left,right])
				self.bytes=wav_bytes
				self.length=len(wav_bytes)

	def new(self,sample_rate,channels,bit_depth,length):
		wav_bytes=[]
		self.channels=channels
		self.bit_depth=bit_depth
		self.sample_rate=sample_rate
		for a in range(0,length):
			if channels==1:
				wav_bytes.append(0)
			elif channels==2:
				wav_bytes.append([0,0])
		self.bytes=wav_bytes
		length=len(wav_bytes)
		data_length=length
		if channels==2:
			data_length*=2
		if bit_depth==16:
			data_length*=2
		self.length=length
		self.data_length=data_length

	def save(self,filename):
		wav=bytearray()
		flattened=self.flatten()
		self.data_length=len(flattened)
		file_size=self.data_length+42

		wav.extend("RIFF".encode())

		wav.append(file_size & 255) # file size
		wav.append((file_size>>8) & 255)
		wav.append((file_size>>16) & 255)
		wav.append((file_size>>24) & 255)

		wav.extend("WAVE".encode())
		wav.extend("fmt ".encode())

		wav.append(16) # length of all data before
		wav.append(0)
		wav.append(0)
		wav.append(0)

		wav.append(1) # data type (pcm)
		wav.append(0)

		wav.append(self.channels) # number of channels
		wav.append(0)

		wav.append(self.sample_rate & 255) # sample rate
		wav.append(self.sample_rate>>8)
		wav.append(0)
		wav.append(0)

		# (sample rate*bit depth*channels)/8
		funny_value=(self.sample_rate*self.bit_depth*self.channels)//8
		wav.append(funny_value & 255)
		wav.append((funny_value>>8) & 255)
		wav.append((funny_value>>16) & 255)
		wav.append((funny_value>>24) & 255)

		# (bit depth*channels)/8
		funny_value=(self.bit_depth*self.channels)//8
		wav.append(funny_value & 255)
		wav.append((funny_value>>8) & 255)

		wav.append(self.bit_depth) # bit depth
		wav.append(0)

		wav.extend("data".encode())

		wav.append(self.data_length & 255) # size of data section
		wav.append((self.data_length>>8) & 255)
		wav.append((self.data_length>>16) & 255)
		wav.append((self.data_length>>24) & 255)

		wav.extend(flattened)

		with open(filename,"wb") as file:
			file.write(wav)

	def flatten(self):
		wav_bytes=bytearray()
		for byte in self.bytes:
			if self.bit_depth==8:
				if self.channels==1:
					byte=((byte+32768)>>8) & 255
					wav_bytes.append(byte)
				elif self.channels==2:
					wav_bytes.append(((byte[0]+32768)>>8) & 255)
					wav_bytes.append(((byte[1]+32768)>>8) & 255)
			elif self.bit_depth==16:
				if self.channels==1:
					byte=(byte+65535) & 65535
					wav_bytes.append(byte & 255)
					wav_bytes.append(byte>>8)
				elif self.channels==2:
					left_byte=(byte[0]+65535) & 65535
					wav_bytes.append(left_byte & 255)
					wav_bytes.append(left_byte>>8)
					right_byte=(byte[1]+65535) & 65535
					wav_bytes.append(right_byte & 255)
					wav_bytes.append(right_byte>>8)
		return wav_bytes

	def flattened_byte(self,byte):
		if self.bit_depth==8:
			if self.channels==1:
				byte=((byte+32768)>>8) & 255
			elif self.channels==2:
				byte=(((byte[0]+32768)>>8) & 255,((byte[1]+32768)>>8) & 255)
		elif self.bit_depth==16:
			if self.channels==1:
				byte=(byte+65535) & 65535
				byte=(byte & 255,byte>>8)
			elif self.channels==2:
				left_byte=(byte[0]+65535) & 65535
				right_byte=(byte[1]+65535) & 65535
				byte=((left_byte & 255,left_byte>>8),(right_byte & 255,right_byte>>8))
		return byte

	def seconds_abs(self,sample_rate,seconds):
		return int(sample_rate*seconds)

	def seconds(self,seconds):
		return int(self.sample_rate*seconds)

	def amplify(self,factor):
		for a in range(0,self.length):
			if self.channels==1:
				byte=int(self.bytes[a]*factor)
				byte=max(min(byte,32767),-32768)
				self.bytes[a]=byte
			elif self.channels==2:
				left_byte=int(self.bytes[a][0]*factor)
				right_byte=int(self.bytes[a][1]*factor)
				left_byte=max(min(left_byte,32767),-32768)
				right_byte=max(min(right_byte,32767),-32768)
				self.bytes[a][0]=left_byte
				self.bytes[a][1]=right_byte

	def filter(self,passes):
		for p in range(0,passes):
			if self.channels==1:
				previous_byte=0
			elif self.channels==2:
				previous_byte=[0,0]
			for a in range(0,self.length):
				if self.channels==1:
					self.bytes[a]=(self.bytes[a]+previous_byte)//2
				elif self.channels==2:
					self.bytes[a][0]=(self.bytes[a][0]+previous_byte[0])//2
					self.bytes[a][1]=(self.bytes[a][1]+previous_byte[1])//2
				previous_byte=self.bytes[a]

	def copy(self):
		wave=Wave()
		wave.new(sample_rate=self.sample_rate,channels=self.channels,bit_depth=self.bit_depth,length=self.length)
		wave.bytes=self.bytes.copy()
		return wave

	def clear(self):
		for a in range(0,self.length):
			if self.channels==1:
				self.bytes[a]=0
			else:
				self.bytes[a]=[0,0]

	def timestretch(self,block_size,percent):
		percent/=100
		new_length=self.length*percent
		step_amount=(1/percent)*block_size
		bytes_temp=self.bytes.copy()
		position=0
		self.bytes.clear()
		while position<self.length:
			position_int=int(position)
			for a in range(position_int,position_int+block_size):
				if a<len(bytes_temp):
					if self.channels==1:
						self.bytes.append(bytes_temp[a])
					elif self.channels==2:
						self.bytes.append([bytes_temp[a][0],bytes_temp[a][1]])
			position+=step_amount
		self.length=len(self.bytes)

	def echo(self,length,decay,bend=0,extend=False):
		iterations=0
		volume=1
		while round(volume,2)>0:
			iterations+=1
			volume*=decay
		if extend:
			if decay<1:
				add_length=self.seconds(length)*iterations
				for a in range(0,add_length):
					if self.channels==1:
						self.bytes.append(0)
					elif self.channels==2:
						self.bytes.append([0,0])
				self.length=len(self.bytes)
			else:
				print("WARNING: Decay is 1, not extending ending...")

		echo_wave=self.copy()
		self.clear()
		position=0
		rate=self.sample_rate
		for a in range(0,iterations):
			if rate>0:
				self.paste(source=echo_wave,dest_pos=self.seconds(position),rate=rate)
				position+=length
				rate+=bend
				echo_wave.amplify(decay)

	def get_nearest_zero_pos(self,pos,sensitivity=1):
		found=False
		if self.channels==1:
			while pos<self.length and not found:
				byte=self.bytes[pos]//sensitivity
				if byte>=-1 and byte<=1:
					found=True
				pos+=1
		elif self.channels==2:
			while pos<self.length and not found:
				byte=((self.bytes[pos][0]//sensitivity)+(self.bytes[pos][1]//sensitivity))//2
				if byte>=-1 and byte<=1:
					found=True
				pos+=1
		return pos

	def set_raw_length(self):
		self.raw_length=int(self.length*(self.sample_rate/self.length))
		if self.channels==2:
			self.raw_length*=2
		if self.bit_depth==16:
			self.raw_length*=2

	def resample(self,rate):
		bytes_temp=self.bytes.copy()
		step_rate=self.sample_rate/rate
		pos=0
		self.bytes.clear()
		while int(pos)<len(bytes_temp):
			if self.channels==1:
				self.bytes.append(bytes_temp[int(pos)])
			elif self.channels==2:
				self.bytes.append([bytes_temp[int(pos)][0],bytes_temp[int(pos)][1]])
			pos+=step_rate
		self.length=len(self.bytes)
		self.set_raw_length()
		self.sample_rate=rate

	def normalize(self):
		peak=0
		factor=1
		for byte in self.bytes:
			if self.channels==2:
				byte=(byte[0]+byte[1])//2
			if abs(byte)>abs(peak):
				peak=abs(byte)
		if peak!=0:
			factor=32768/peak
		for a in range(0,self.length):
			if self.channels==1:
				self.bytes[a]*=factor
				self.bytes[a]=int(self.bytes[a])
			elif self.channels==2:
				self.bytes[a][0]*=factor
				self.bytes[a][1]*=factor
				self.bytes[a][0]=int(self.bytes[a][0])
				self.bytes[a][1]=int(self.bytes[a][1])

	def fade(self,region):
		region_samples=(self.seconds(region[0]),self.seconds(region[1]))
		pos=0
		for a in range(0,region_samples[0]):
			factor=a/region_samples[0]
			if self.channels==1:
				self.bytes[a]*=factor
				self.bytes[a]=int(self.bytes[a])
			elif self.channels==2:
				self.bytes[a][0]*=factor
				self.bytes[a][1]*=factor
				self.bytes[a][0]=int(self.bytes[a][0])
				self.bytes[a][1]=int(self.bytes[a][1])
			pos+=1
		for a in range(region_samples[1],self.length):
			factor=(0-((a-region_samples[1])/(self.length-region_samples[1])))+1
			if self.channels==1:
				self.bytes[a]*=factor
				self.bytes[a]=int(self.bytes[a])
			elif self.channels==2:
				self.bytes[a][0]*=factor
				self.bytes[a][1]*=factor
				self.bytes[a][0]=int(self.bytes[a][0])
				self.bytes[a][1]=int(self.bytes[a][1])
			pos+=1

	def plaster(self,wave,amount,seconds,warble=0,amplify=1):
		if isinstance(wave,Wave):
			length=self.seconds_abs(wave.sample_rate,seconds)
			wave.amplify(amplify)
			for a in range(0,amount):
				if warble:
					rate=random.randint(wave.sample_rate-warble,wave.sample_rate+warble)
				else:
					rate=wave.sample_rate
				self.paste(wave,random.randint(0,length-wave.length),rate=rate)
		elif isinstance(wave,list) or isinstance(wave,tuple):
			waves=[]
			for a in wave:
				if isinstance(a,Wave):
					a.amplify(amplify)
					waves.append(a)
				else:
					wav=Wave()
					wav.open(a)
					wav.amplify(amplify)
					waves.append(wav)
			sample_rate=0
			bit_depth=0
			channels=0
			for a in waves:
				if a.sample_rate>sample_rate or a.bit_depth>bit_depth or a.channels>channels:
					sample_rate=a.sample_rate
					bit_depth=a.bit_depth
					channels=a.channels
			length=self.seconds_abs(sample_rate,seconds)
			for a in range(0,amount):
				wave_rand=random.choice(waves)
				if warble:
					rate=random.randint(wave_rand.sample_rate-warble,wave_rand.sample_rate+warble)
				else:
					rate=wave_rand.sample_rate
				self.paste(wave_rand,random.randint(0,length-wave_rand.length),rate=rate)

	def paste(self,source,dest_pos,source_range=(0,0),rate=0,clip=True,join=False):
		if dest_pos<self.length:
			source_pos=source_range[0]
			source_length=source_range[1]
			if source_length==0:
				source_length=len(source.bytes)
			if rate==0:
				rate=source.sample_rate
			source_inc_amount=rate/self.sample_rate
			source_length=int(source_length/source_inc_amount)
			for a in range(dest_pos,dest_pos+source_length):
				source_pos_int=int(source_pos)
				if source_pos_int>source.length-1:
					source_pos_int=source.length-1
					if source.channels==1:
						source_byte=0
					elif source.channels==2:
						source_byte=[0,0]
				else:
					source_byte=source.bytes[source_pos_int]
				if join:
					if a<self.length:
						if source.channels==1:
							if self.channels==1: # source mono, dest mono
								self.bytes.append(source_byte)
							elif self.channels==2: # source mono, dest stereo
								self.bytes.append([source_byte,source_byte])
						elif source.channels==2:
							if self.channels==1: # source stereo, dest mono
								self.bytes.append(source_byte[0])
							elif self.channels==2: # source stereo, dest stereo
								self.bytes.append(source_byte)
				else:
					if a<self.length:
						if source.channels==1:
							if self.channels==1: # source mono, dest mono
								if a>0:
									byte=self.bytes[a]+source_byte
								else:
									byte=self.bytes[0]+source_byte
							elif self.channels==2: # source mono, dest stereo
								if a>0:
									left_byte=self.bytes[a][0]+source_byte
									right_byte=self.bytes[a][1]+source_byte
								else:
									left_byte=self.bytes[0][0]+source_byte
									right_byte=self.bytes[0][1]+source_byte
						elif source.channels==2:
							if self.channels==1: # source stereo, dest mono
								if a>0:
									byte=self.bytes[a]+source_byte[0]
								else:
									byte=self.bytes[0]+source_byte[0]
							elif self.channels==2: # source stereo, dest stereo
								if a>0:
									left_byte=self.bytes[a][0]+source_byte[0]
									right_byte=self.bytes[a][1]+source_byte[1]
								else:
									left_byte=self.bytes[0][0]+source_byte[0]
									right_byte=self.bytes[0][1]+source_byte[1]
				source_pos+=source_inc_amount
				
				if join:
					self.length=len(self.bytes)
				else:
					if clip:
						if self.channels==1:
							byte=max(min(byte,32767),-32768)
						elif self.channels==2:
							left_byte=max(min(left_byte,32767),-32768)
							right_byte=max(min(right_byte,32767),-32768)
					else:
						if self.channels==1:
							byte//=2
						elif self.channels==2:
							left_byte//=2
							right_byte//=2
					if a<self.length and a>0:
						if self.channels==1:
							self.bytes[a]=byte
						elif self.channels==2:
							self.bytes[a][0]=left_byte
							self.bytes[a][1]=right_byte
			