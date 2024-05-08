# Funksjon som finner klipppepunktene ved å bruke TransNetV2
# Tar inn liste med navn på alle videoene
def klippepunkt(videoer):
    f = open(videoer, "r")
    h = f.readlines()

    for line in h:  # går igjennom en og en linje
        if line.startswith('ï»¿'):
            line = line[3:]
        if line.endswith('\n'):
            line = line[:-1]
        kommando = "python TransNetV2/inference/transnetv2.py " + line
        subprocess.run(kommando, shell=True)


# Funksjon som konverterer klippepunktene i en video fra 'frames' til sekunder
# Tar inn en liste med navn på alle filene med klippepunkter laget av TransNet
def konvertere(frames):
    f = open(frames, "r")
    u = open("sekunder.txt", "w")
    h = f.readlines()
    tall = ''

    for file in h:  # går igjennom en og en fil

        if file.startswith('ï»¿'):  # Sørger for at formatet til filen ikke ødelegger fil-navnet
            file = file[3:]
        modified_file = file[:-1]  # Ignorerer det siste tegnet
        fi = open(modified_file, "r")
        fil = fi.readlines()

        # Går igjennom filen med frames og gjør det om til en linje med sekunder
        for line in fil:
            for k in line:
                if k == ' ' or k == '\n':
                    if k == '\n':
                        tall = round(int(tall) / 25, 3)
                        u.write(str(tall) + ",")
                    tall = ''

                else:
                    tall = tall + k
        u.write("\n")
        fi.close()

        # Sletter filene laget av transNet
        os.remove(modified_file)
        modified_file = modified_file[:-10] + 'predictions.txt'
        os.remove(modified_file)

    f.close()  # lukker filen
    u.close()


# Funksjon som tar inn tidsbegrensning og filer med videonavn og klippepunkter, og klipper sammen til en video
def lim(videoer, sekunder, tid):
    ut = open('vi.txt', 'w')  # Filen som skal brukes i ffmpeg
    vid = open(videoer, 'r')  # Listen med videoer
    f = open(sekunder, 'r')  # Klippepunkter i videoene
    linjer = f.readlines()

    tidbrukt = 0
    i = -1
    # Oppretter filen som skal brukes i ffmpeg ved å gå igjennom listene og legge til de første
    # videoklippene fra hver video frem til tidsbegrensningen er nådd.
    while tidbrukt < tid:
        for linje in linjer:
            klippepunkter = linje.strip().split(',')  # Deler tidene opp til hvert element
            if i < (len(klippepunkter) - 2):  # Sjekker at det er igjen flere klipp
                # Finner frem riktige klippepunkt
                if i == -1:
                    klipp = ['0', klippepunkter[0]]
                else:
                    klipp = klippepunkter[i:i + 2]

                # Avslutter når tidsgrensen blir nådd
                tidbrukt = tidbrukt + (float(klipp[1]) - float(klipp[0]))
                if tidbrukt >= tid:
                    break

                # Legger inn teksten i filen
                navn = vid.readline().rstrip('\n')
                if navn.startswith('ï»¿'):
                    navn = navn[3:]
                ut.write("file '" + navn + "'\n")
                ut.write('inpoint ' + klipp[0] + '\n')
                ut.write('outpoint ' + klipp[1] + '\n')

            else:
                vid.readline()
        # Går til starten av listene igjen
        f.seek(0)
        vid.seek(0)
        i = i + 1

    # Husker på å lukke filene
    ut.close()
    vid.close()
    f.close()

    # Bruker ffmpeg til å lime sammen klippene
    kommando = "ffmpeg -f concat -safe 0 -i vi.txt -c copy utVideo.mp4"
    subprocess.run(kommando, shell=True)


if __name__ == '__main__':
    import subprocess
    import sys
    import os

    # Input fra terminalen
    videoer = sys.argv[1]
    tidsbegrensning = int(sys.argv[2])

    klippepunkt(videoer)    # Finner klippepunktene på videoene

    # Lager en liste med navn på alle filene som inneholder klipp funnet av TransNet
    kommando = ['powershell', '-Command',
                'Get-ChildItem -Filter *.mp4.scenes.txt | ForEach-Object { "$($_.Name)" } | '
                'Out-File -Encoding utf8 frames.txt']
    subprocess.run(kommando, shell=True)

    konvertere('frames.txt')    # Gjør om klippepunktene fra frames til sekunder

    lim(videoer, 'sekunder.txt', tidsbegrensning)   # Limer sammen klippene frem til tidsbegrensningen er nådd

    # sletter de midlertidige filene
    os.remove("frames.txt")
    os.remove("vi.txt")
    os.remove("sekunder.txt")
