import unittest
from maksukortti import Maksukortti

class TestMaksukortti(unittest.TestCase):
    def setUp(self):
        self.maksukortti = Maksukortti(1000)


    def test_luotu_kortti_on_olemassa(self):
        self.assertNotEqual(self.maksukortti, None)

    def test_saldo_alustuu(self):
        self.assertEqual(self.maksukortti.saldo_euroina(), 10)

    def test_saldo_kasvaa_oikein(self):
        self.maksukortti.lataa_rahaa(1000)
        self.assertEqual(self.maksukortti.saldo_euroina(), 20)

    def test_saldo_vähenee_oikein(self):
        self.maksukortti.ota_rahaa(500)
        self.assertEqual(self.maksukortti.saldo_euroina(), 5)

    def test_saldo_ei_muutu_jos_ei_rahaa(self):
        self.maksukortti.ota_rahaa(20000)
        self.assertEqual(self.maksukortti.saldo_euroina(), 10)

    def test_ota_rahaa_palauttaa_onnistumisen_oikein(self):
        self.assertEqual(self.maksukortti.ota_rahaa(500), True)

    def test_ota_rahaa_palauttaa_epäonnistumisen_oikein(self):
        self.assertEqual(self.maksukortti.ota_rahaa(50000), False)

    def test_str_toimii(self):
        self.assertEqual(str(self.maksukortti), "Kortilla on rahaa 10.00 euroa")

if __name__ == "__main__":
    import unittest
    unittest.main()