package edu.bbte.crypto.jdim2141;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.security.cert.Certificate;
import java.security.cert.CertificateParsingException;
import java.security.cert.X509Certificate;
import java.util.Arrays;
import javax.net.ssl.SSLPeerUnverifiedException;
import javax.net.ssl.SSLSocket;
import javax.net.ssl.SSLSocketFactory;
import lombok.extern.slf4j.Slf4j;

@Slf4j
public class TLSClient {

    private static final String BNR_HOST = "bnr.ro";
    private static final Integer SERVER_PORT = 443;
    private static final String OUTPUT_FILE = "bnr-home.html";


    public static void main(String[] args) {
        log.info("Main started");
        try (Socket socket = SSLSocketFactory.getDefault().createSocket(BNR_HOST, SERVER_PORT)) {
            printCertificates(socket);

            var outputStream = socket.getOutputStream();

            log.info("Socket connection made");
            PrintWriter printWriter = new PrintWriter(outputStream, true, StandardCharsets.UTF_8);
            printWriter.println("GET /Home.aspx HTTP/1.1");
            printWriter.println("Host: " + BNR_HOST);
            printWriter.println("Connection: close");
            printWriter.println();

            log.info("Get request sent");
            var inputStream = socket.getInputStream();
            var inputStreamReader = new InputStreamReader(inputStream);

            try (BufferedReader in = new BufferedReader(inputStreamReader);
                var writeOut = new BufferedWriter((new FileWriter(OUTPUT_FILE)))
            ) {
                String line;
                boolean startWriting = false;

                while((line = in.readLine()) != null) {

                    if (line.contains("<!DOCTYPE")) {
                        startWriting = true;
                    }

                    if (startWriting) {
                        writeOut.write(line);
                        writeOut.write("\n");
                    }
                }
            }
        } catch (UnknownHostException e) {
            log.error("Unknown Error: {}", e.getMessage());
        } catch (IOException e) {
            log.error("Io exception", e);
        }
        log.error("HTML got");
    }

    private static void printCertificates(Socket socket) throws SSLPeerUnverifiedException {
        var sslSession = ((SSLSocket) socket).getSession();

        Certificate[] certificates = sslSession.getPeerCertificates();
        for (Certificate certificate: certificates) {
            try {
                if (certificate instanceof X509Certificate cert) {
                    System.out.println("-".repeat(50));
                    System.out.println("Version: " + cert.getVersion());
                    System.out.println("Serial number: " + cert.getSerialNumber());
                    System.out.println("Issuer Name: " + cert.getIssuerX500Principal());
                    System.out.println("Not Before: " + cert.getNotBefore()); // issued at
                    System.out.println("Not After: " + cert.getNotAfter()); // valid until
                    System.out.println("Subject Name: " + cert.getSubjectX500Principal());
                    System.out.println(
                        "Subject Alternative Names: " + cert.getSubjectAlternativeNames());
                    System.out.println(
                        "Public key algorithm: " + cert.getPublicKey().getAlgorithm());
                    System.out.println("Public key: " + cert.getPublicKey());
                }
            } catch (CertificateParsingException e) {
                log.error("Parsing exception", e);
            }
        }

        System.out.println("-".repeat(50));
    }
}
