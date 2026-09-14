import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from fastapi.testclient import TestClient


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with patch.dict(os.environ, {'DATABASE_URL': ''}):
            spec = importlib.util.spec_from_file_location('catalog_api', Path(__file__).parents[1] / 'main.py')
            cls.api = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cls.api)
        cls.client = TestClient(cls.api.app)
        cls.temp = tempfile.TemporaryDirectory()
        cls.api.CATALOG_PATH = Path(cls.temp.name) / 'catalog.json'
        records = []
        for city, price, rooms, area in [('São Paulo', 500000, 2, 75), ('São Paulo', 800000, 3, 100), ('Piracicaba', 300000, None, None)]:
            records.append(dict(cidade=city, uf='SP', bairro='Centro', preco=price, area=area, quartos=rooms,
                banheiros=None, vagas=None, link=f'https://example.com/{price}', imobiliaria='Teste', tipo='Apartamento'))
        cls.api.CATALOG_PATH.write_text(json.dumps(dict(last_update='2026-09-14', properties=records)))

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_same_neighborhood_does_not_mix_cities(self):
        result = self.client.get('/api/properties', params={'cidade': 'São Paulo', 'bairro': 'Centro'}).json()
        self.assertEqual(result['total'], 2)
        self.assertTrue(all(p['cidade'] == 'São Paulo' for p in result['properties']))

    def test_filters_and_pagination(self):
        result = self.client.get('/api/properties', params={'cidade': 'São Paulo', 'per_page': 1, 'page': 2}).json()
        self.assertEqual(result['total_pages'], 2)
        self.assertEqual(result['properties'][0]['preco'], 800000)
        result = self.client.get('/api/properties', params={'cidade': 'São Paulo', 'preco_max': 600000, 'quartos': 2}).json()
        self.assertEqual(result['total'], 1)

    def test_missing_features_not_excluded_with_zero_filters(self):
        result = self.client.get('/api/properties').json()
        self.assertEqual(result['total'], 1)
        self.assertIsNone(result['properties'][0]['area'])

    def test_unknown_city_empty_and_invalid_filters_rejected(self):
        self.assertEqual(self.client.get('/api/properties?cidade=Unknown').json()['total'], 0)
        self.assertEqual(self.client.get('/api/properties?page=0').status_code, 422)
        self.assertEqual(self.client.get('/api/properties?preco_max=-1').status_code, 422)

    def test_sp_prediction_is_rejected(self):
        response = self.client.post('/api/predict', json=dict(cidade='São Paulo', bairro='Centro', area=75, quartos=2, banheiros=1, vagas=1))
        self.assertEqual(response.status_code, 400)

    def test_missing_catalog_is_service_unavailable(self):
        with patch.object(self.api, 'CATALOG_PATH', Path(self.temp.name) / 'missing.json'):
            self.assertEqual(self.client.get('/api/properties').status_code, 503)

    def test_geo_handles_catalog_without_known_areas(self):
        self.assertEqual(self.client.get('/api/geo').status_code, 200)


if __name__ == '__main__':
    unittest.main()
