## Generate a self signed certificate

- Step 1 -> Generate the certificate identical with bnr.ro-s certificate

- openssl req\
    -newkey rsa:2048\           // Generating the new private key
    -sha256\
    -keyout BNR_private.key\    // Private key output file
    -x509\                      // Generating the certificate
    -days 365\                  // Expiration day for certificate
    -subj "/CN=*.bnr.ro/O=Banca Nationala a Romaniei/L=Bucuresti/ST=Bucuresti/C=RO"\ // Subject the format is required from SSL
    -passout pass:password\     // To be not prompted for the PEM phrase                                   
    -out BNR_server.crt         // The certificate containing file 

- Step 2 -> 
