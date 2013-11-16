# from hello import app
import os
import sokapi
import unittest
import tempfile
import json
from sokapi import get_map_name


class UtilsTestCase(unittest.TestCase):
    def test_get_map_name(self):
        self.assertEqual(get_map_name(1), '001.obj')
        self.assertEqual(get_map_name(10), '010.obj')
        self.assertEqual(get_map_name(999), '999.obj')
        self.assertEqual(get_map_name(1199), '1199.obj')
        self.assertEqual(get_map_name(-99), '099.obj')


class SokapiTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, sokapi.app.config['DATABASE'] = tempfile.mkstemp()
        sokapi.app.config['TESTING'] = True
        self.app = sokapi.app.test_client()
        sokapi.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(sokapi.app.config['DATABASE'])

    def test_post_get_results(self):
        self.app.post(
            '/api/v1/result/243',
            method='POST',
            data=dict(
                moves=40,
                time=2000,
                user='mario'
            ),
            follow_redirects=False
        )
        self.app.post(
            '/api/v1/result/243',
            method='POST',
            data=dict(
                moves=40,
                time=3000,
                user='wario'
            ),
            follow_redirects=False
        )
        presp = self.app.post(
            '/api/v1/result/243',
            method='POST',
            data=dict(
                moves=20,
                time=6000,
                user='luigi'
            ),
            follow_redirects=True
        )
        resp = self.app.get('/api/v1/result/243')
        resp_empty = self.app.get('/api/v1/result/111')
        resp = json.loads(resp.response.next())
        presp = json.loads(presp.response.next())
        resp_empty = json.loads(resp_empty.response.next())
        self.assertEqual(resp, presp)
        self.assertEqual(resp['1']['user'], 'luigi')
        self.assertEqual(resp['2']['user'], 'mario')
        self.assertEqual(resp['3']['user'], 'wario')
        self.assertEqual(len(resp_empty), 0)

    def test_get_map(self):
        with open('./maps/999999.obj', 'w') as fw:
            fw.write('0000ffff')
        resp = self.app.get(
            '/api/v1/map/999999'
        )
        self.assertEqual(resp.response.next(), '0000ffff')

    def test_post_result_fail(self):
        resp = self.app.post(
            '/api/v1/result/243',
            method='POST',
            data=dict(
                moves=40,
                time=2000,
            ),
            follow_redirects=True
        )
        self.assertEqual(resp.status_code, 400)

if __name__ == '__main__':
    unittest.main()
