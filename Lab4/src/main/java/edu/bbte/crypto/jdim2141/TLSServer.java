package edu.bbte.crypto.jdim2141;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.KeyStore;
import java.security.NoSuchAlgorithmException;
import java.security.cert.CertificateException;
import javax.net.ssl.KeyManagerFactory;
import javax.net.ssl.SSLContext;
import javax.net.ssl.SSLServerSocket;
import javax.net.ssl.SSLServerSocketFactory;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TLSServer {

    private static final char[] PASSWORD = "password".toCharArray();
    private static final Integer SERVER_PORT = 443;
    private static final String INPUT_HTML = "bnr-home.html";
    private static final String KEYSTORE = "BNR_keystore.jks";

    public static void main(String[] args) {
        log.info("Server initialization started...");

        try {
            var keyStore = KeyStore.getInstance("JKS");

            try (var keyStoreInputStream = new FileInputStream(KEYSTORE)) {
                keyStore.load(keyStoreInputStream, PASSWORD);
            } catch (FileNotFoundException e) {
                log.error("Keystore file not found", e);
            } catch (IOException e) {
                log.error("Io exception", e);
            } catch (CertificateException | NoSuchAlgorithmException e) {
                log.error("Certificate exception", e);
            }

            KeyManagerFactory keyManagerFactory = KeyManagerFactory.getInstance("SunX509");
            keyManagerFactory.init(keyStore, PASSWORD);

            SSLContext sslContext = SSLContext.getInstance("TLS");
            sslContext.init(keyManagerFactory.getKeyManagers(), null, null);

            SSLServerSocketFactory sslServerSocketFactory = sslContext.getServerSocketFactory();

            try (var serverSocket = (SSLServerSocket) sslServerSocketFactory.createServerSocket(SERVER_PORT)) {
                log.info("Server is running on PORT=" + SERVER_PORT);
                String htmlContent = readHtmlContent();
                while (true) {
                    try (var clientSocket = serverSocket.accept()) {
                        log.info("Connection from: {}", clientSocket.getInetAddress());
                        handleClientConnection(clientSocket, htmlContent);
                    } catch (IOException e) {
                        log.error("Io exception", e);
                    }
                }
            }
        } catch (Exception e) {
            log.error("Key store exception", e);
        }
    }

    private static void handleClientConnection(Socket clientSocket, String htmlContent) throws IOException {
        try (var inReader = new BufferedReader(new InputStreamReader(clientSocket.getInputStream()))) {
            var out = clientSocket.getOutputStream();

            String line;
            while((line = inReader.readLine()) != null) {
                log.info(line);
            }

            String response = "HTTP/1.1 200 OK\r\n" +
                "Content-Type: text/html\r\n" +
                "Content-Length: " + htmlContent.getBytes().length + "\r\n" +
                "\r\n" +
                htmlContent;

            out.write(response.getBytes());
            out.flush();

            log.info("Response HTML sent");
        }
    }

    private static String readHtmlContent() {
        var path = Paths.get(INPUT_HTML);
        try {
            String content = Files.readString(path, StandardCharsets.UTF_8);
            log.info("Html content read. Length is: {}", content.length());
            return content;
        } catch (IOException e) {
            log.error("Unable to read html content");
            throw new RuntimeException(e);
        }
    }
}
