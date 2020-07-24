import random
import sys

from OpenSSL import crypto


def create_root():
    public_key = crypto.PKey()
    public_key.generate_key(crypto.TYPE_RSA, 4096)

    certificate = crypto.X509()
    certificate.set_version(3)
    certificate.set_serial_number(int(random.random() * sys.maxsize))
    certificate.gmtime_adj_notBefore(0)
    certificate.gmtime_adj_notAfter(60 * 60 * 24 * 365)  # 1 year

    certificate_subject = certificate.get_subject()
    certificate_subject.CN = "example.com"
    certificate_subject.O = "mycommonname"

    certificate_issuer = certificate.get_issuer()
    certificate_issuer.CN = "example.com"
    certificate_issuer.O = "mycommonname"

    certificate.set_pubkey(public_key)
    certificate.add_extensions([
        crypto.X509Extension(b"basicConstraints", True,
                             b"CA:TRUE"),
        crypto.X509Extension(b"subjectKeyIdentifier", False, b"hash",
                             subject=certificate)
    ])
    certificate.add_extensions([
        crypto.X509Extension(b"authorityKeyIdentifier", False, b"keyid:always",
                             issuer=certificate)
    ])

    certificate.sign(public_key, "sha1")

    with open("Certificate/root.pem", "wb") as certfile:
        certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, certificate))
        certfile.close()

    with open("Certificate/root.key", "wb") as pkeyfile:
        pkeyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, public_key))
        pkeyfile.close()


def create_certificate(cn, o, server_side, cert_file_name, pkey_file_name):
    rootpem = open("Certificate/root.pem", "rb").read()
    rootkey = open("Certificate/root.key", "rb").read()
    ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, rootpem)
    ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, rootkey)

    pkey = crypto.PKey()
    pkey.generate_key(crypto.TYPE_RSA, 2048)

    cert = crypto.X509()
    cert.set_serial_number(int(random.random() * sys.maxsize))
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(60 * 60 * 24 * 365)
    cert.set_version(3)

    subject = cert.get_subject()
    subject.CN = cn
    subject.O = o

    if server_side:
        cert.add_extensions([crypto.X509Extension(b"subjectAltName", False,
                                                  b"DNS:test1.example.com,DNS:test2.example.com")])

    cert.set_issuer(ca_cert.get_subject())

    cert.set_pubkey(pkey)
    cert.sign(ca_key, "sha1")

    with open(cert_file_name, "wb") as certfile:
        certfile.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        certfile.close()

    with open(pkey_file_name, "wb") as pkeyfile:
        pkeyfile.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey))
        pkeyfile.close()


print("Making root CA")
create_root()
print("Making server certificate")
create_certificate("server", "my organisation", True, "Certificate/server.crt", "Certificate/server.key")
print("Making client certificate")
create_certificate("client", "my organisation", False, "Certificate/client.crt", "Certificate/client.key")
