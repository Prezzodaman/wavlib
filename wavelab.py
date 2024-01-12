from wavlib import Wave
import os
import pyaudio

def index_key(dictionary,index):
	return list(dictionary)[index]

def input_float(prompt,num_range=None):
	valid=False
	if num_range!=None:
		prompt+=f"({num_range[0]}-{num_range[1]}) "
	while not valid:
		choice=input(prompt)
		if choice.replace(".","").replace("-","").isdigit():
			if num_range==None:
				valid=True
				return float(choice)
			else:
				if float(choice)>=num_range[0] and float(choice)<=num_range[1]:
					valid=True
					return float(choice)

def input_number(prompt,num_range=None):
	valid=False
	if num_range!=None:
		prompt+=f"({num_range[0]}-{num_range[1]}) "
	while not valid:
		choice=input(prompt)
		if choice.replace("-","").isdigit():
			if num_range==None:
				valid=True
				return int(choice)
			else:
				if int(choice)>=num_range[0] and int(choice)<=num_range[1]:
					valid=True
					return int(choice)

def input_yes_no(prompt):
	choice=""
	while choice.lower()!="y" and choice.lower()!="n":
		choice=input(f"{prompt} (y/n) ")
	return choice.lower()=="y"

def play_sound(sound,region):
	pya=pyaudio.PyAudio()
	start=region[0]
	end=region[1]
	if end==0:
		end=sound.length
	stream=pya.open(format=pya.get_format_from_width(sound.bit_depth//8),channels=sound.channels,rate=sound.sample_rate,output=True,frames_per_buffer=2**5)
	for a in range(start,end):
		byte=sound.flattened_byte(sound.bytes[a])
		if isinstance(byte,int):
			stream.write(byte.to_bytes(1))
		elif isinstance(byte,tuple):
			if isinstance(byte[0],tuple):
				ray=[byte[0][0],byte[0][1],byte[1][0],byte[1][1]]
			else:
				ray=[byte[0],byte[1]]
			stream.write(bytes(ray))
	stream.close()
	pya.terminate()

def show_sound_list(sounds):
	for counter,sound in enumerate(sounds.keys()):
		name=sound
		sound=sounds[sound]
		bit_depth=sound.bit_depth
		if sound.channels==1:
			mono_stereo="mono"
		elif sound.channels==2:
			mono_stereo="stereo"
		seconds=round(sound.length/sound.sample_rate,2)
		sample_rate=sound.sample_rate
		print(f"{str(counter+1).rjust(2,' ')}) {name} ({sample_rate} Hz, {bit_depth}-bit, {mono_stereo}, {seconds} seconds)")

print(" --== WaVeLaB 0.1 ==--")
print("by Presley Peters, 2023")
print()
wave_temp=Wave()
choice=1
sounds={}

while choice!=0:
	print("- Main Menu - ")
	print()
	print(" 1) Add a sound to the list")
	print(" 2) Remove a sound from the list")
	print(" 3) View the sound list")
	print(" 4) Operate on a sound")
	print(" 5) Open a project")
	print(" 6) Save a project")
	print(" 7) Quick play")
	print(" 8) Help")
	print(" 0) Exit")
	choice=input_number("Choose option: ",num_range=(0,8))
	print()
	if choice==1:
		choice=""
		while choice.lower()!="o" and choice.lower()!="n" and choice.lower()!="c":
			print("- Add Sound -")
			print()
			choice=input("(O)pen a sound, create a (N)ew one or (C)ancel? ")
		if choice.lower()!="c":
			if choice.lower()=="o":
				choice_valid=False
				while not choice_valid:
					choice=input("Enter filename of the sound to open: ")
					if choice!="":
						if (choice[0]=="'" and choice[-1]=="'") or (choice[0]=="\"" and choice[-1]=="\""):
							choice=choice[1:-1]
						if choice.split(".")[-1].lower()=="wav":
							if os.path.exists(choice):
								choice_valid=True
							else:
								print("File doesn't exist!")
						else:
							print("Only wave files are supported!")
				name=choice.split(".")[0].split("/")[-1]
				counter=0
				for a in sounds.keys():
					if a.lower().startswith(name.lower()):
						counter+=1
				if counter>0:
					name=f"{name}{counter}"
					print(f"A sound already exists with that name - renaming to {name}...")
				sounds.update({name:Wave()})
				print("Opening sound...")
				sounds[name].open(choice)
				if sounds[name].bit_depth>16:
					del sounds[name]
					print("Only 8-bit and 16-bit sounds are supported!")
			else:
				sample_rate=input_number("Enter sample rate: ")

				choice=""
				while choice!="8" and choice!="16":
					choice=input("Enter bit depth (8, 16): ")
				bit_depth=int(choice)

				length=wave_temp.seconds_abs(sample_rate,input_number("Enter length (in seconds): "))

				choice=""
				while choice.lower()!="m" and choice.lower()!="s":
					choice=input("(M)ono or (S)tereo? ")
				if choice.lower()=="m":
					channels=1
				else:
					channels=2

				choice=""
				while choice=="":
					choice=input("Enter name: ")

				sounds.update({choice:Wave()})
				sounds[choice].new(sample_rate=sample_rate,bit_depth=bit_depth,channels=channels,length=length)
				print("New sound created!")
	if choice==2:
		choice=""
		if len(sounds)==0:
			print("No sounds to remove!")
		else:
			print("- Remove Sound -")
			print()
			show_sound_list(sounds)
			print()
			choice_valid=False
			while not choice_valid:
				choice=input("Which sound number to remove? (0 for none) ")
				if choice.isdigit():
					if int(choice)>=0 and int(choice)<=len(sounds):
						choice_valid=True
			if int(choice)>0:
				del sounds[index_key(sounds,int(choice)-1)]
				print("Sound removed!")
	elif choice==3:
		if len(sounds)==0:
			print("Sound list empty!")
		else:
			print("- Sound List -")
			print()
			show_sound_list(sounds)
	elif choice==4:
		if len(sounds)==0:
			print("Sound list empty!")
		else:
			print("- Sound Surgery -")
			print()
			show_sound_list(sounds)
			print()
			choice=input_number("Select sound to operate on (0 for none): ",num_range=(0,len(sounds)))
			if choice>0:
				current_sound=index_key(sounds,choice-1)
				choice=""
				choice_valid=False
				print()
				print(" 1) Trim\t\t- trims/removes a section from this sound")
				print(" 2) Reverse\t\t- reverses this sound")
				print(" 3) Layer\t\t- layers a sound on top of this one")
				print(" 4) Join\t\t- appends a sound to the end of this one")
				print(" 5) Amplify\t\t- increases/decreases the overall volume")
				print(" 6) Plaster\t\t- \"plasters\" one or more sounds across this one")
				print(" 7) Play region\t\t- plays a section")
				print(" 8) Duplicate\t\t- makes a copy")
				print(" 9) Save\t\t- saves this sound to a file")
				print("10) Echo\t\t- adds a delay effect")
				print("11) Change sample rate\t- changes the sample rate, affecting the speed")
				print("12) Resample\t\t- changes the sample rate, preserving the speed")
				print("13) Bend\t\t- makes the speed increase/decrease at a certain rate")
				print("14) Normalize\t\t- brings the overall volume to its loudest")
				print("15) Erase\t\t- clears the entire sound")
				print("16) Time stretch\t- changes the speed without affecting pitch")
				print("17) Pitch shift\t\t- changes the pitch without affecting speed")
				print("18) Fade\t\t- gradually increases/decreases the volume")
				print("19) Rename\t\t- change the name of this sound")
				print("20) Filter\t\t- softens the high-end of this sound")
				if sounds[current_sound].channels==1:
					print("21) Convert to stereo\t- you figure it out")
				elif sounds[current_sound].channels==2:
					print("21) Convert to mono\t- you figure it out")
				print(" 0) Nothing")
				print()
				choice=input_number("Select operation: ",num_range=(0,21))
				if choice>0:
					print()
				if choice==1:
					try_again=True
					start=0
					seconds=sounds[current_sound].length/sounds[current_sound].sample_rate
					end=round(seconds,2)
					seconds=round(seconds,2)
					length=round(seconds,2)
					print("- Trim -")
					print()
					while try_again:
						print(f"Sample length: {seconds} seconds, trim start: {start} seconds, trim end: {end} seconds")
						start=input_float("Set start point: ",num_range=(0,length))
						end=input_float("Set end point: ",num_range=(start,length))
						zero=input_yes_no("Nearest zero crossings?")
						choice=""
						play=True
						while play:
							if choice.lower()!="t" and choice.lower()!="r" and choice.lower()!="a" and choice.lower()!="c":
								choice=input("(T)rim outside region, (R)emove inside region, Try (A)gain, (P)lay Region, (C)ancel ")
							if choice.lower()=="t" or choice.lower()=="r":
								start=sounds[current_sound].seconds(start)
								end=sounds[current_sound].seconds(end)
								if zero:
									start=sounds[current_sound].get_nearest_zero_pos(start,sensitivity=8)
									end=sounds[current_sound].get_nearest_zero_pos(end,sensitivity=8)
								if choice.lower()=="r":
									sounds[current_sound].bytes=sounds[current_sound].bytes[:start]+sounds[current_sound].bytes[end:]
								else:
									sounds[current_sound].bytes=sounds[current_sound].bytes[start:end]
								sounds[current_sound].length=len(sounds[current_sound].bytes)
								try_again=False
								play=False
							if choice.lower()=="p":
								play_sound(sounds[current_sound],(sounds[current_sound].seconds(start),sounds[current_sound].seconds(end)))
							if choice.lower()=="c":
								try_again=False
								play=False
							if choice.lower()=="a":
								play=False
				elif choice==2:
					print("- Reverse -")
					sounds[current_sound].bytes.reverse()
					print("Sound reversed!")
				elif choice==3:
					print("- Layer -")
					print()
					show_sound_list(sounds)
					print()

					choice=input_number("Select sound to layer: ",num_range=(1,len(sounds)))
					current_sound_layer=index_key(sounds,choice-1)

					start=input_float("Set start point for layered sound: ",num_range=(0,sounds[current_sound].length))
					length=input_float("Set length of layered sound: (0 for full sound) ",num_range=(0,sounds[current_sound_layer].length))
					if length==0:
						length=sounds[current_sound_layer].length
					else:
						length=sounds[current_sound].seconds(length)

					rate=input_number("Set sample rate of layered sound: (0 for original) ")
					if rate==0:
						rate=sounds[current_sound_layer].sample_rate

					start=sounds[current_sound].seconds(start)
					sounds[current_sound].paste(source=sounds[current_sound_layer],dest_pos=start,source_range=(0,length),rate=rate)
					print("Sound layered!")
				elif choice==4:
					print("- Join -")
					show_sound_list(sounds)
					print()

					choice=input_number("Join which sound? ",num_range=(1,len(sounds)))
					current_sound_join=index_key(sounds,choice-1)

					if current_sound==current_sound_join:
						current_sound_temp=sounds[current_sound].copy()
						sounds[current_sound].paste(source=current_sound_temp,dest_pos=0,join=True)
					else:
						sounds[current_sound].paste(source=sounds[current_sound_join],dest_pos=0,join=True)
					print("Sound joined!")

				elif choice==5:
					print("- Amplify -")
					print()
					sounds[current_sound].amplify(input_float("Amplify by how much? ",num_range=(0,16)))
					print()
					print("Sound amplified!")
				elif choice==6:
					print("- Plaster -")
					print()
					choice=""
					one=False
					while choice.lower()!="o" and choice.lower()!="m":
						choice=input("Plaster (O)ne sound or (M)ultiple sounds? ")
					show_sound_list(sounds)
					print()
					if choice.lower()=="o":
						one=True
						current_sound_plaster=current_sound
						while current_sound_plaster==current_sound:
							choice=input_number("Plaster which sound? ",num_range=(1,len(sounds)))
							current_sound_plaster=index_key(sounds,choice-1)
							if current_sound_plaster==current_sound:
								print("Can't plaster a sound onto itself!")
					else:
						choice_valid=False
						current_sound_plaster=[]
						plaster_list=[]
						while not choice_valid:
							print("Plaster list:",", ".join(plaster_list))
							choice=input("Enter a sample number to add to the list, or just press enter to continue: ")
							if choice=="":
								if len(current_sound_plaster)==0:
									print("List can't be empty!")
								else:
									choice_valid=True
							if choice.isdigit():
								if int(choice)>=1 and int(choice)<=len(sounds):
									name=index_key(sounds,int(choice)-1)
									if name==current_sound:
										print("Can't plaster a sound onto itself!")
									else:
										if not sounds[name] in current_sound_plaster:
											current_sound_plaster.append(sounds[name])
											plaster_list.append(name)

					amount=input_number("How much? ",num_range=[1,10000])
					seconds=input_number("For how many seconds? ",num_range=[1,round(sounds[current_sound].length/sounds[current_sound].sample_rate,2)])
					warble=input_number("Sample rate deviation: ")
					amplify=input_float("Amplify by how much? ")

					if one:
						sounds[current_sound].plaster(sounds[current_sound_plaster],amount,seconds,warble=warble,amplify=amplify)
					else:
						sounds[current_sound].plaster(current_sound_plaster,amount,seconds,warble=warble,amplify=amplify)
					print()
					print("Plastered!")
				elif choice==7:
					print("- Play -")
					print()
					play=True
					while play:
						seconds=round(sounds[current_sound].length/sounds[current_sound].sample_rate,2)
						start=input_float(f"Start point: (0-{seconds}) ",num_range=(0,seconds))
						end=input_float(f"End point: ({start}-{seconds}) ",num_range=(start,seconds))
						print("Playing...")
						play_sound(sounds[current_sound],(sounds[current_sound].seconds(start),sounds[current_sound].seconds(end)))
						print()
						play=input_yes_no("Play again?")
				elif choice==8:
					print("- Duplicate -")
					print()
					choice=""
					choice_valid=False
					while not choice_valid:
						choice=input("Enter new name: ")
						if choice!="":
							found=False
							for sound in sounds:
								if sound==choice:
									print("Sound already exists with that name!")
									found=True
							choice_valid=not found
					sounds.update({choice:sounds[current_sound].copy()})
					print("Sound duplicated!")
				elif choice==9:
					print("- Save -")
					print()
					choice_valid=False
					while not choice_valid:
						choice=input("Enter filename: ")
						if choice[0]=="'" and choice[-1]=="'":
							choice=choice[1:-2]
							print(choice)
						choice_valid=True
						if choice.split(".")[-1].lower()!="wav":
							choice+=".wav"
					sounds[current_sound].save(choice)
					print("Sound saved!")
				elif choice==10:
					print("- Echo -")
					print()
					length=input_float("Enter echo length: ")
					decay=input_float("Enter decay amount: ",num_range=(0,1))
					bend=input_number("Enter bend amount: ")
					extend=input_yes_no("Extend ending?")
					sounds[current_sound].echo(length=length,decay=decay,bend=bend,extend=extend)
					print()
					print("Sound echoed!")
				elif choice==11:
					print("- Sample Rate -")
					print()
					print(f"Original sample rate: {sounds[current_sound].sample_rate}")
					rate=input_number("Enter new sample rate: ")
					sounds[current_sound].sample_rate=rate
					print("Sample rate adjusted!")
				elif choice==12:
					print("- Resample -")
					print()
					print(f"Original sample rate: {sounds[current_sound].sample_rate}")
					rate=input_number("Enter new sample rate: ")
					sounds[current_sound].resample(rate)
					print()
					print("Sound resampled!")
				elif choice==13:
					print("- Bend -")
					print()
					rate=input_float("Bend how much up or down? (can be a decimal) ")
					bytes_temp=sounds[current_sound].bytes.copy()
					pos=0
					bend_rate=sounds[current_sound].sample_rate
					sounds[current_sound].bytes.clear()
					while int(pos)<len(bytes_temp) and bend_rate>0:
						step_rate=bend_rate/sounds[current_sound].sample_rate
						bend_rate+=rate
						if sounds[current_sound].channels==1:
							sounds[current_sound].bytes.append(bytes_temp[int(pos)])
						elif sounds[current_sound].channels==2:
							sounds[current_sound].bytes.append([bytes_temp[int(pos)][0],bytes_temp[int(pos)][1]])
						pos+=step_rate
					sounds[current_sound].length=len(sounds[current_sound].bytes)
					sounds[current_sound].set_raw_length()
					print()
					print("Sound bent!")
				elif choice==14:
					print("- Normalize -")
					print()
					sounds[current_sound].normalize()
					print()
					print("Sound normalized!")
				elif choice==15:
					print("- Erase -")
					print()
					if input_yes_no("Are you sure?"):
						sounds[current_sound].clear()
						print("Sound erased!")
					else:
						print("Erasure cancelled...")
				elif choice==16:
					print("- Time Stretch -")
					print()
					block_size=input_number("Enter block size (in samples): ",num_range=(1,sounds[current_sound].length))
					percent=input_number("Enter stretch percentage: ",num_range=(1,2000))
					sounds[current_sound].timestretch(block_size=block_size,percent=percent)
					print()
					print("Sound stretched!")
				elif choice==17:
					print("- Pitch Shift -")
					print()
					block_size=input_number("Enter block size (in samples): ",num_range=(1,sounds[current_sound].length))
					semitones=input_float("Enter semitones: ",num_range=(-24,24))
					percent=(1.0595**semitones)*100
					resample=input_yes_no("Resample?")
					sounds[current_sound].timestretch(block_size=block_size,percent=percent)
					old_rate=sounds[current_sound].sample_rate
					sounds[current_sound].sample_rate=int(sounds[current_sound].sample_rate*(2**(semitones/12)))
					if resample:
						sounds[current_sound].resample(old_rate)
					print()
					print("Pitch shifted!")
				elif choice==18:
					print("- Fade -")
					print()
					seconds=round(sounds[current_sound].length/sounds[current_sound].sample_rate,2)
					print(f"Sample length: {seconds} seconds")
					fade_in=input_float("Fade in to: ",num_range=(0,seconds))
					fade_out=input_float("Fade out from: ",num_range=(fade_in,seconds))
					sounds[current_sound].fade((fade_in,fade_out))
					print()
					print("Sound faded!")
				elif choice==19:
					print("- Rename -")
					print()
					choice=input("Input new name: (or leave blank to cancel) ")
					if choice!="":
						sounds[choice]=sounds[current_sound]
						del sounds[current_sound]
				elif choice==20:
					print("- Filter -")
					print()
					passes=input_number("Enter number of passes: ",num_range=(1,64))
					sounds[current_sound].filter(passes)
					print()
					print("Sound filtered!")
				elif choice==21:
					if sounds[current_sound].channels==1:
						print("- Convert to Stereo -")
						print()
						sounds[current_sound].channels=2
						for a in range(0,sounds[current_sound].length):
							byte=sounds[current_sound].bytes[a]
							sounds[current_sound].bytes[a]=[byte,byte]
						print()
						print("Done!")
					elif sounds[current_sound].channels==2:
						print("- Convert to Mono -")
						print()
						choice=""
						while choice.lower()!="l" and choice.lower()!="r" and choice.lower()!="m":
							choice=input("(L)eft Channel, (R)ight Channel, (M)ix Both? ")
						sounds[current_sound].channels=1
						if choice.lower()!="l":
							for a in range(0,sounds[current_sound].length):
								byte=sounds[current_sound].bytes[a][0]
								sounds[current_sound].bytes[a]=byte
						elif choice.lower()!="r":
							for a in range(0,sounds[current_sound].length):
								byte=sounds[current_sound].bytes[a][1]
								sounds[current_sound].bytes[a]=byte
						elif choice.lower()!="m":
							for a in range(0,sounds[current_sound].length):
								byte=(sounds[current_sound].bytes[a][0]+sounds[current_sound].bytes[a][1])//2
								sounds[current_sound].bytes[a]=byte
						print()
						print("Done!")
				choice=1
			choice=1
	elif choice==5:
		print("- Open Project -")
		print()
		choice_valid=False
		while not choice_valid:
			choice=input("Enter filename of the project to open: (or nothing to cancel) ")
			if choice=="":
				choice_valid=True
			else:
				if len(choice.split("."))==2:
					if choice.split(".")[-1].lower()!="wlp":
						choice+=".wlp"
					if os.path.exists(choice):
						if os.path.isdir(choice.split(".")[-2]):
							choice_valid=True
						else:
							print("Associated folder doesn't exist!")
					else:
						print("File doesn't exist!")
				else:
					print("Invalid filename format!")
		if choice!="":
			sounds.clear()
			error=False
			with open(choice,"r") as file:
				for counter,line in enumerate(file.readlines()):
					line=line.strip("\n")
					sound_filename=line.split(".")[0]
					sounds.update({sound_filename:Wave()})
					filename=(choice.split(".")[-2]+"/"+line).replace("//","/")
					try:
						print(f"Opening {filename}...")
						sounds[sound_filename].open(filename)
					except:
						print(f"Failed to open {filename}!")
						del sounds[sound_filename]
						error=True
			print()
			if error:
				print("Project opened (with errors)")
			else:
				print("Project opened!")
	elif choice==6:
		print("- Save Project -")
		print()
		choice_valid=False
		while not choice_valid:
			choice=input("Enter filename of the project to save: (or nothing to cancel) ")
			if choice=="":
				choice_valid=True
			else:
				if len(choice.split("."))==2:
					if choice.split(".")[-1].lower()=="wlp":
						choice_valid=True
					else:
						print("File must have the extension: .wlp")
				else:
					print("Invalid filename format!")
		if choice!="":
			error=False
			try:
				project=[]
				path=choice.split(".")[0].replace("/","")
				os.mkdir(path)
				for name,wave in zip(sounds.keys(),sounds.values()):
					print(f"Saving {path}/{name}.wav...")
					wave.save(f"{path}/{name}.wav")
					project.append(f"{name}.wav")
				with open(choice,"w") as file:
					file.write("\n".join(project))
				print()
				print("Project Saved!")
			except:
				print("Some error occured!")
	elif choice==7:
		if len(sounds)==0:
			print("Sound list empty!")
		else:
			print("- Quick Play -")
			print()
			show_sound_list(sounds)
			print()
			choice=input_number("Select sound to play (0 for none): ",num_range=(0,len(sounds)))
			if choice>0:
				current_sound=index_key(sounds,choice-1)
				choice=True
				if sounds[current_sound].length/sounds[current_sound].sample_rate>30:
					choice=input_yes_no("This is a long sound - really play it in full?")
				if choice:
					print("Playing...")
					play_sound(sounds[current_sound],(0,sounds[current_sound].length))
			choice=1
	elif choice==8:
		print("- Help -")
		print()
		print("* For convenience, units of time are measured in *seconds*, not samples")
		print("* Amplify factors are given as decimals, for example:")
		print("  * 1 for normal volume")
		print("  * 2 for double the volume")
		print("  * 0.5 for half the volume")
		print("* Bend/warble amounts are given in terms of sample rates (or Hz)")
		print("  * Using a value of 10 in the Bend effect will increase the rate by 10 Hz for every sample")
		print("  * Using a warble value of 500 in the Plaster effect will vary the rate between +500 Hz and -500 Hz")
		print("* Sample rate changing is uninterpolated, so if it sounds crusty, that's why")
		print("* A project file must have a folder with the same name (minus the extension) associated with it!")
		print("* Lots of operations are slow, because I wrote this program")
		print("* There's no undo ;)")
		print()
		input("Press enter when done...")
		choice=1
	elif choice==0:
		choice=input_yes_no("Are you sure?")
		if choice:
			choice=0
		else:
			choice=1
	print()
print("Goodbyte :)")