## Generate a self signed certificate

- **Step 1** -> Generate the certificate identical with bnr.ro-s certificate

```bash
# -newkey -> Generating the new private key
# -keyout -> Private key output file
# -x509   -> Certificate type 
# -days   -> expiration day 
# -subj   -> The format is required by openssl(the attributes to be separated by a '/')
# -passout -> If we doesnt add a password here, the openssl will propmt us to give a PEM key
openssl req \
    -newkey rsa:2048 \           
    -sha256 \
    -keyout BNR_private.key \    
    -x509 \                      
    -days 365 \                  
    -subj "/CN=*.bnr.ro/O=Banca Nationala a Romaniei/L=Bucuresti/ST=Bucuresti/C=RO" \ 
    -passout pass:password \      phrase                                   
    -out BNR_server.crt 
``` 
- Step 2 -> Export the certificate into the pkcs12 format, which contains the private key beside the certificate 
```bash
openssl pkcs12 \
  -export \
  -name bnr_keystore \
  -in BNR_server.crt \
  -inkey BNR_private.key \
  -out BNR_crt_key.p12 \
  -passin pass:password \
  -passout pass:password
```

## Part 3

### Generate RootCA

#### Step 1 

- Generate a key using the elliptic curve encryption key with 256 long key
```bash
openssl ecparam \
  -name prime256v1 \
  -out rootCA.key \
  -genkey
```

#### Step 2

- Generate the RootCA certificate 
```bash
openssl req \
  -new \
  -x509 \
  -days 28 \
  -subj "/C=RO/ST=Kolozs/L=Kolozsvár/O=BBTE/CN=jdim2141-RootCA" \
  -key rootCA.key \
  -sha256 \
  -passout pass:password \
  -out RootCA.crt
```

### Generate ServerCA 

#### Step 1 

- Generate a key using the elliptic curve
```bash
openssl ecparam \
    -name prime256v1 \
    -out serverCA.key \
    -genkey
```

#### Step 2

- Generate the ServerCA certificate request
```bash
openssl req \
  -new \
  -subj "/C=RO/ST=Kolozs/L=Kolozsvár/O=BBTE/CN=jdim2141-ServerCA" \
  -key serverCA.key \
  -sha256 \
  -passout pass:password \
  -out serverCA.csr
```

#### Step 3

- Generate the ServerCA certificate signed by RootCA
```bash
openssl x509 \
  -req \
  -in serverCA.csr \
  -CA RootCA.crt \
  -CAkey rootCA.key \
  -days 28 \
  -CAcreateserial \
  -sha256 \
  -passin pass:password \
  -out ServerCA.crt
```

### Generate ClientCA

#### Step 1

- Generate a key using the elliptic curve
```bash
openssl ecparam \
  -name prime256v1 \
  -out clientCA.key \
  -genkey
```

#### Step 2

- Generate the ClientCA certificate request

```bash
openssl req \
  -new \
  -subj "/C=RO/ST=Kolozs/L=Kolozsvár/O=BBTE/CN=jdim2141-ClientCA" \
  -key clientCA.key \
  -sha256 \
  -passout pass:password \
  -out clientCA.csr
```

#### Step 3

- Generate the ClientCA certificate signed by RootCA
```bash
openssl x509 \
  -req \
  -in clientCA.csr \
  -CA RootCA.crt \
  -CAkey rootCA.key \
  -days 28 \
  -CAcreateserial \
  -sha256 \
  -passin pass:password \
  -out ClientCA.crt
```

## Part 4

### Generate certificate for Client 

- Generate a key for client 
```bash
openssl ecparam \
  -name prime256v1 \
  -out client.key \
  -genkey
```

- Generate certificate request for the Client
```bash
openssl req \
  -new \
  -subj "/C=RO/ST=Kolozs/L=Kolozsvár/O=BBTE/CN=jdim2141-client" \
  -key client.key \
  -sha256 \
  -passout pass:password \
  -out client.csr
```

- Generate certificate singed by ClientCA 
```bash
openssl x509 \
  -req \
  -in client.csr \
  -CA ClientCA.crt \
  -CAkey clientCA.key \
  -days 28 \
  -CAcreateserial \
  -sha256 \
  -passin pass:password \
  -out client.crt
```

## Part 5

### Generate certificate for Server 

- Generate a key for server 
```bash
openssl ecparam \
  -name prime256v1 \
  -out server.key \
  -genkey
```

- Generate certificate request for the Server 
```bash
openssl req \
  -new \
  -subj "/C=RO/ST=Kolozs/L=Kolozsvár/O=BBTE/CN=jdim2141-server" \
  -key server.key \
  -sha256 \
  -passin pass:password \
  -out server.csr
```

- Generate certificate signed by ServerCA 
```bash
openssl x509 \
  -req \
  -in server.csr \
  -CA ServerCA.crt \
  -CAkey serverCA.key \
  -days 28 \
  -CAcreateserial \
  -sha256 \
  -passin pass:password \
  -out server.crt 
``` 

## Part 6

- Create server's keystore

```bash
openssl pkcs12 \
  -export \
  -in server.crt \
  -inkey server.key \
  -out server_crt_key.p12 \
  -passin pass:password \
  -passout pass:password \
  -name server_keystore
```

- Import keystore from pkcs12 keystore

```bash
keytool -importkeystore \
  -destkeystore server_keystore.jks \
  -srckeystore server_crt_key.p12 \
  -srcstoretype PKCS12 \
  -srcstorepass password \
  -alias server_keystore \
  -deststorepass password \
  -destkeypass password
```

- Setup client truststore 

```bash
keytool -importcert \
  -file ServerCA.crt \
  -keystore client_truststore.jks \
  -keypass password \
  -storepass password 
```
