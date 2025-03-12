import unittest
from kassapaate import Kassapaate
from maksukortti import Maksukortti

class TestKassapaate(unittest.TestCase):
    def setUp(self):
        self.kassapaate = Kassapaate()
        self.maksukortti = Maksukortti(500)

    def test_alkuarvot_oikein(self):
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.edulliset + self.kassapaate.maukkaat, 0)
        
    def test_kateinen_edullisesti_maksu_onnistuu(self):
        vaihtoraha = self.kassapaate.syo_edullisesti_kateisella(500)

        self.assertEqual(vaihtoraha, 260)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1002.4)
        self.assertEqual(self.kassapaate.edulliset, 1)

    def test_kateinen_maukas_maksu_onnistuu(self):
        vaihtoraha = self.kassapaate.syo_maukkaasti_kateisella(500)

        self.assertEqual(vaihtoraha, 100)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1004)
        self.assertEqual(self.kassapaate.maukkaat, 1)

    def test_kateinen_edullisesti_maksu_epäonnistuu(self):
        vaihtoraha = self.kassapaate.syo_edullisesti_kateisella(100)

        self.assertEqual(vaihtoraha, 100)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)

    def test_kateinen_maukas_maksu_epäonnistuu(self):
        vaihtoraha = self.kassapaate.syo_maukkaasti_kateisella(100)

        self.assertEqual(vaihtoraha, 100)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_maksukortti_edullisesti_maksu_onnistuu(self):
        tulos = self.kassapaate.syo_edullisesti_kortilla(self.maksukortti)

        self.assertEqual(tulos, True)
        self.assertEqual(self.maksukortti.saldo_euroina(), 2.6)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.edulliset, 1)

    def test_maksukortti_maukas_maksu_onnistuu(self):
        tulos = self.kassapaate.syo_maukkaasti_kortilla(self.maksukortti)

        self.assertEqual(tulos, True)
        self.assertEqual(self.maksukortti.saldo_euroina(), 1)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.maukkaat, 1)

    def test_maksukortti_edullisesti_maksu_epäonnistuu(self):
        self.maksukortti = Maksukortti(100)
        tulos = self.kassapaate.syo_edullisesti_kortilla(self.maksukortti)

        self.assertEqual(tulos, False)
        self.assertEqual(self.maksukortti.saldo_euroina(), 1)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.edulliset, 0)

    def test_maksukortti_maukas_maksu_epäonnistuu(self):
        self.maksukortti = Maksukortti(100)
        tulos = self.kassapaate.syo_maukkaasti_kortilla(self.maksukortti)

        self.assertEqual(tulos, False)
        self.assertEqual(self.maksukortti.saldo_euroina(), 1)
        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.kassapaate.maukkaat, 0)

    def test_kortille_lataus_onnistuu(self):
        self.kassapaate.lataa_rahaa_kortille(self.maksukortti, 100)

        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1001)
        self.assertEqual(self.maksukortti.saldo_euroina(), 6)

    def test_kortille_lataus_epäonnistuu(self):
        self.kassapaate.lataa_rahaa_kortille(self.maksukortti, -5)

        self.assertEqual(self.kassapaate.kassassa_rahaa_euroina(), 1000)
        self.assertEqual(self.maksukortti.saldo_euroina(), 5)
