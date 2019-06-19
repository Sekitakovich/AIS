import ftplib

if __name__ == '__main__':

    # server = 'localhost'
    # user = 'pi'
    # passwd = 'sekitakovich'

    server = 'www.c-quick.net'
    user = 'k-seki'
    passwd = 'poti,y2'

    ftp = ftplib.FTP(server)

    ftp.login(user=user, passwd=passwd)

    files = ftp.nlst('.')
    for f in files:
        print(f)

    # ooo = ftp.mlsd()
    # for name, info in ooo:
    #     print(name)

    ftp.close()
