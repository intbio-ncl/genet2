import sys
import os
import unittest
from rdflib import Graph,URIRef,Literal
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.enhancer.data_miner.database.handler import DatabaseHandler

class TestDatabaseHandler(unittest.TestCase):

    def setUp(self):
        self.db_handler = DatabaseHandler()

    def tearDown(self):
        None
    
    def _atleast_one(self,expectant,graph):
        for triple in graph:
            for element in triple:
                if str(expectant) in str(element):
                    return True
                if str(expectant) == str(element):
                    return True
        return False

    def test_handler_get_db_names_sbh_bba(self):
        sbh_bba_identities = [URIRef("https://synbiohub.org/public/igem/BBa_B0034/1"),
                             URIRef("https://synbiohub.org/public/igem/BBa_B0012/1"),
                             URIRef("https://synbiohub.org/public/igem/BBa_B0010/1"),
                             URIRef("http://parts.igem.org/Part:BBa_C0040"),
                             "BBa_B0015",
                             "BBa_A101",
                             "BBa_J23100"]

        expected_dbs = [self.db_handler.synbiohub]
        for identity in sbh_bba_identities:
            actual_dbs = self.db_handler._get_potential_db_names(identity)
            self.assertCountEqual(expected_dbs,actual_dbs)

    def test_handler_get_db_names_sbh_non_bba(self):
        sbh_bba_identities = [URIRef("https://synbiohub.org/public/igem/scar/1"),
                              "synbiohub_scar"]

        expected_dbs = [self.db_handler.synbiohub]
        for identity in sbh_bba_identities:
            actual_dbs = self.db_handler._get_potential_db_names(identity)
            self.assertCountEqual(expected_dbs,actual_dbs)

    def test_handler_get_db_names_gbk(self):
        gbk_identifiers = [URIRef("https://www.ncbi.nlm.nih.gov/nuccore/KJ775863.1"),
                        URIRef("https://www.ncbi.nlm.nih.gov/protein/SYZ34079.1")]

        expected_dbs = [self.db_handler.genbank]
        for identity in gbk_identifiers:
            actual_dbs = self.db_handler._get_potential_db_names(identity)
            self.assertCountEqual(expected_dbs,actual_dbs)
    
    def test_handler_get_db_names_unknown(self):
        sbh_bba_identities = [URIRef("https://www.uniprot.org/uniprot/A0A1D8DF22"),
                                "laci",
                                "tetr"]
        expected_dbs = [self.db_handler.synbiohub,self.db_handler.genbank,self.db_handler.sevahub,self.db_handler.lcp]
        for identity in sbh_bba_identities:
            actual_dbs = self.db_handler._get_potential_db_names(identity)
            self.assertCountEqual(expected_dbs,actual_dbs)

    def test_handler_get_sbh_exists_uri(self):
        shb_identity = URIRef("https://synbiohub.org/public/igem/BBa_C0051/1")
        record = self.db_handler.get(shb_identity)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one("BBa_C0051",record))

    def test_handler_get_sbh_exists_name(self):
        shb_identity = "BBa_K389004"
        record = self.db_handler.get(shb_identity)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one("BBa_K389004",record))

    def test_handler_get_sbh_no_exist(self):
        shb_identity = URIRef("https://synbiohub.org/public/igem/BBa_C005111/1")
        record = self.db_handler.get(shb_identity)
        self.assertIsNone(record)

    def test_handler_get_gbk_exists_uri(self):
        gbk_identity = URIRef("https://www.ncbi.nlm.nih.gov/nuccore/U02897.1")
        record = self.db_handler.get(gbk_identity)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one("U02897.1",record))

    def test_handler_get_gbk_exists_name(self):
        gbk_identity = "MT436494.1"
        record = self.db_handler.get(gbk_identity)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(gbk_identity,record))

    def test_handler_get_gbk_no_exist(self):
        gbk_identity = URIRef("https://www.ncbi.nlm.nih.gov/nuccore?term=MTT436494.1")
        record = self.db_handler.get(gbk_identity)
        self.assertIsNone(record)

    def test_handler_get_sbh_rdflib_uri(self):
        shb_identity = URIRef("https://synbiohub.org/public/igem/BBa_C005111/1")
        record = self.db_handler.get(shb_identity)



    def test_handler_count_match_single(self):
        query_strings = ["T1","tetracycline","BBa_E1010","LuxI"]
        for query_string in query_strings:
            cumulative_count = 0
            for count in self.db_handler.count(query_string):
                self.assertIsInstance(count,int)
                cumulative_count = cumulative_count + count
            self.assertGreater(cumulative_count,0)

    def test_handler_count_match_multiple(self):
        query_strings = ["double terminator","lacI repressor" ,"tetracycline repressor","TetR repressible promoter"]
        for query_string in query_strings:
            cumulative_count = 0
            for count in self.db_handler.count(query_string):
                self.assertIsInstance(count,int)
                cumulative_count = cumulative_count + count
            self.assertGreater(cumulative_count,0)

    def test_handler_count_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_query_match"]
        for query_string in query_strings:
            for count in self.db_handler.count(query_string):
                self.assertIsInstance(count,int)
                self.assertEqual(count,0)

    def test_handler_count_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            for count in self.db_handler.count(query_string):
                self.assertIsInstance(count,int)
                self.assertEqual(count,0)

    def test_handler_query_match_single(self):
        query_strings = ["T1","GFP","laci"]
        for query_string in query_strings:
            for results in self.db_handler.query(query_string):
                self.assertGreater(len(results),0,query_string)

    def test_handler_query_match_multiple(self):
        query_strings = ["double terminator","lacI repressor" ,"tetracycline repressor","TetR repressible promoter"]
        for query_string in query_strings:
            cumulative_count = 0
            for results in self.db_handler.query(query_string):
                cumulative_count = cumulative_count + len(results)
            self.assertGreater(cumulative_count,0)

    def test_handler_query_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_query_match"]
        for query_string in query_strings:
            for results in self.db_handler.query(query_string):
                self.assertEqual(len(results),0)

    def test_handler_query_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            for results in self.db_handler.query(query_string):
                self.assertEqual(len(results),0)

    def test_is_record(self):
        sbh = ["https://synbiohub.org/public/igem/BBa_K144401511/1",
               "https://synbiohub.org/public/igem//1",
               "BBa_K144401511",
               "https://synbiohub.org/public/igem/BBa_K1444015"]
        for s in sbh:
            self.assertFalse(self.db_handler.is_record(s))
        sbh = ["https://synbiohub.org/public/igem/BBa_K1444015/1",
               "http://sevahub.es/public/Canonical/cd_T1/1",
               "https://synbiohub.programmingbiology.org/public/Cello_VPRGeneration_Paper/v2_circuit_0x06_5_S1_SrpR/1"]
        for s in sbh:
            self.assertTrue(self.db_handler.is_record(s))

    def test_sequence_search(self):
        sequence = "ccaggcatcaaataaaacgaaaggctcagtcgaaagactgggcctttcgttttatctgttgtttgtcggtgaacgctctc"
        res = self.db_handler.sequence_search(sequence)
        for r in res:
            r = URIRef(r)
            record = self.db_handler.get(r)
            seq_o = list(record.triples((r,URIRef("http://sbols.org/v2#sequence"),None)))[0][2]
            seq = list(record.triples((seq_o,URIRef("http://sbols.org/v2#elements"),None)))[0][2]
            self.assertEqual(str(seq),sequence)

    def test_get_uri(self):
        name = "BBa_K1444016"
        res = self.db_handler.get_uri(name)
        self.assertTrue(name in res)

        name = "Non_entity"
        res = self.db_handler.get_uri(name)
        self.assertIsNone(res)

    



class TestDatabaseHandlerSynbiohub(unittest.TestCase):

    def setUp(self):
        self.db_handler = DatabaseHandler()
        sbh_interface_name = self.db_handler.synbiohub
        self.sbh_interface = self.db_handler._db_util.db_mapping_calls[sbh_interface_name]

    def tearDown(self):
        None
    
    def _atleast_one(self,expectant,graph):
        for triple in graph:
            for element in triple:
                if str(expectant) in str(element):
                    return True
                if str(expectant) == str(element):
                    return True
        return False

    def test_synbiohub_interface_get_id(self):
        sbh_id = "BBa_K1653004"
        record = self.sbh_interface.get(sbh_id)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(sbh_id,record))
        
    def test_synbiohub_interface_get_uri(self):
        sbh_uri = URIRef("https://synbiohub.org/public/Digitalizer/all_or_nothing/1")
        record = self.sbh_interface.get(sbh_uri)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(sbh_uri,record))

    def test_synbiohub_interface_get_no_prune(self):
        sbh_id = "BBa_K1653004"
        p_record = self.sbh_interface.get(sbh_id,prune=True)
        record = self.sbh_interface.get(sbh_id,prune=False)
        self.assertGreater(record,p_record)

    def test_synbiohub_interface_get_id_no_record(self):
        self.assertRaises(ValueError, self.sbh_interface.get,"BBa_K16530044")

    def test_synbiohub_interface_get_uri_no_record(self):
        sbh_uri = URIRef("https://synbiohub.org/public/bsu/module_BO_30843_encodes_BO_112399/1")
        self.assertRaises(ValueError, self.sbh_interface.get,sbh_uri)
     
    def test_synbiohub_interface_query_match_single(self):
        query_strings = ["laci","ptetr","pbad","gfp"]
        for query_string in query_strings:
            results = self.sbh_interface.query(query_string)
            self.assertGreater(len(results),0)

    def test_synbiohub_interface_query_match_multiple(self):
        query_strings = ["laci repressor","ptetr repressible promoter","pbad inducible","gfp fluorescent"]
        for query_string in query_strings:
            results = self.sbh_interface.query(query_string)
            self.assertGreater(len(results),0)

    def test_synbiohub_interface_query_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_match"]
        for query_string in query_strings:
            results = self.sbh_interface.query(query_string)
            self.assertEqual(len(results),0)

    def test_synbiohub_interface_query_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            results = self.sbh_interface.query(query_string)
            self.assertEqual(len(results),0)

    def test_synbiohub_interface_count_match_single(self):
        query_strings = ["elowitz","T1","luxR","pBad"]
        for query_string in query_strings:
            count = self.sbh_interface.count(query_string)
            self.assertGreater(count,0)

    def test_synbiohub_interface_count_match_multiple(self):
        query_strings = ["elowitz RBS","T1 64 bp","pBad araC","luxR repressor activator"]
        for query_string in query_strings:
            count = self.sbh_interface.count(query_string)
            self.assertGreater(count,0)

    def test_synbiohub_interface_count_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_match"]
        for query_string in query_strings:
            count = self.sbh_interface.count(query_string)
            self.assertEqual(count,0)

    def test_synbiohub_interface_count_no_match_multiple(self):
        query_strings = ["elowitz no_match_here","T1 64 atvg","pBad random_word","luxR repressor no_match"]
        for query_string in query_strings:
            count = self.sbh_interface.count(query_string)
            self.assertEqual(count,0)


class TestDatabaseHandlerSevahub(unittest.TestCase):

    def setUp(self):
        self.db_handler = DatabaseHandler()
        sevahub_interface_name = self.db_handler.sevahub
        self.svh_interface = self.db_handler._db_util.db_mapping_calls[sevahub_interface_name]

    def tearDown(self):
        None
    
    def _atleast_one(self,expectant,graph):
        for triple in graph:
            for element in triple:
                if str(expectant) in str(element):
                    return True
                if str(expectant) == str(element):
                    return True
        return False

    def test_sevahub_interface_get_id(self):
        sbh_id = "GFP"
        record = self.svh_interface.get(sbh_id)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(sbh_id,record))

    def test_sevahub_interface_get_uri(self):
        sbh_id = "http://sevahub.es/public/Canonical/cd_Cm/1"
        record = self.svh_interface.get(sbh_id)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(sbh_id,record))

    def test_sevahub_interface_get_no_prune(self):
        sbh_id = "cd_Cm"
        p_record = self.svh_interface.get(sbh_id,prune=True)
        record = self.svh_interface.get(sbh_id,prune=False)
        self.assertGreater(record,p_record)

    def test_sevahub_interface_get_id_no_record(self):
        self.assertRaises(ValueError, self.svh_interface.get,"BBa_K16530044")

    def test_sevahub_interface_get_uri_no_record(self):
        sbh_uri = URIRef("https://synbiohub.org/public/bsu/module_BO_30843_encodes_BO_112399/1")
        self.assertRaises(ValueError, self.svh_interface.get,sbh_uri)
     
    def test_sevahub_interface_query_match_single(self):
        query_strings = ["laci","RK2","pbad","gfp"]
        for query_string in query_strings:
            results = self.svh_interface.query(query_string)
            self.assertGreater(len(results),0)

    def test_sevahub_interface_query_match_multiple(self):
        query_strings = ["seva Streptomycin","Seva AscI"]
        for query_string in query_strings:
            results = self.svh_interface.query(query_string)
            self.assertGreater(len(results),0,query_string)

    def test_sevahub_interface_query_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_match"]
        for query_string in query_strings:
            results = self.svh_interface.query(query_string)
            self.assertEqual(len(results),0)

    def test_sevahub_interface_query_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            results = self.svh_interface.query(query_string)
            self.assertEqual(len(results),0)

    def test_sevahub_interface_count_match_single(self):
        query_strings = ["lac","T1","lux","pBad"]
        for query_string in query_strings:
            count = self.svh_interface.count(query_string)
            self.assertGreater(count,0,query_string)

    def test_sevahub_interface_count_match_multiple(self):
        query_strings = ["pBad araC","seva Streptomycin","seva PshAI"]
        for query_string in query_strings:
            count = self.svh_interface.count(query_string)
            self.assertGreater(count,0,query_string)

    def test_sevahub_interface_count_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_match"]
        for query_string in query_strings:
            count = self.svh_interface.count(query_string)
            self.assertEqual(count,0)

    def test_sevahub_interface_count_no_match_multiple(self):
        query_strings = ["elowitz no_match_here","T1 64 atvg","pBad random_word","luxR repressor no_match"]
        for query_string in query_strings:
            count = self.svh_interface.count(query_string)
            self.assertEqual(count,0)


class TestDatabaseHandlerLCPHub(unittest.TestCase):

    def setUp(self):
        self.db_handler = DatabaseHandler()
        lcp_interface_name = self.db_handler.lcp
        self.lcp_interface = self.db_handler._db_util.db_mapping_calls[lcp_interface_name]

    def tearDown(self):
        None
    
    def _atleast_one(self,expectant,graph):
        for triple in graph:
            for element in triple:
                if str(expectant) in str(element):
                    return True
                if str(expectant) == str(element):
                    return True
        return False

    def test_lcphub_interface_get_id(self):
        sbh_id = "GFP_protein_production"
        record = self.lcp_interface.get(sbh_id)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(sbh_id,record))
        
    def test_lcphub_interface_get_uri(self):
        sbh_uri = URIRef("https://synbiohub.programmingbiology.org/public/Cello_Parts/AmeR_protein_degradation/1")
        record = self.lcp_interface.get(sbh_uri)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(sbh_uri,record))

    def test_lcphub_interface_get_no_prune(self):
        sbh_id = "pBAD"
        p_record = self.lcp_interface.get(sbh_id,prune=True)
        record = self.lcp_interface.get(sbh_id,prune=False)
        self.assertGreater(record,p_record)

    def test_lcphub_interface_get_id_no_record(self):
        self.assertRaises(ValueError, self.lcp_interface.get,"BBa_K16530044")

    def test_lcphub_interface_get_uri_no_record(self):
        sbh_uri = URIRef("https://synbiohub.org/public/bsu/module_BO_30843_encodes_BO_112399/1")
        self.assertRaises(ValueError, self.lcp_interface.get,sbh_uri)
     
    def test_lcphub_interface_query_match_single(self):
        query_strings = ["laci","cello","pbad","gfp"]
        for query_string in query_strings:
            results = self.lcp_interface.query(query_string)
            self.assertGreater(len(results),0,query_string)

    def test_lcphub_interface_query_match_multiple(self):
        query_strings = ["YFP reporter","v scar","V scar sequence"]
        for query_string in query_strings:
            results = self.lcp_interface.query(query_string)
            self.assertGreater(len(results),0,query_string)

    def test_lcphub_interface_query_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_match"]
        for query_string in query_strings:
            results = self.lcp_interface.query(query_string)
            self.assertEqual(len(results),0)

    def test_lcphub_interface_query_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            results = self.lcp_interface.query(query_string)
            self.assertEqual(len(results),0)

    def test_lcphub_interface_count_match_single(self):
        query_strings = ["T1","luxR","pBad"]
        for query_string in query_strings:
            count = self.lcp_interface.count(query_string)
            self.assertGreater(count,0,query_string)

    def test_lcphub_interface_count_match_multiple(self):
        query_strings = ["HSL LuxR","HSL LuxR protein"]
        for query_string in query_strings:
            count = self.lcp_interface.count(query_string)
            self.assertGreater(count,0,query_string)

    def test_lcphub_interface_count_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_match"]
        for query_string in query_strings:
            count = self.lcp_interface.count(query_string)
            self.assertEqual(count,0)

    def test_lcphub_interface_count_no_match_multiple(self):
        query_strings = ["elowitz no_match_here","T1 64 atvg","pBad random_word","luxR repressor no_match"]
        for query_string in query_strings:
            count = self.lcp_interface.count(query_string)
            self.assertEqual(count,0)

class TestDatabaseHandlerGenbank(unittest.TestCase):

    def setUp(self):
        self.db_handler = DatabaseHandler()
        gbk_interface_name = self.db_handler.genbank
        self.gbk_interface = self.db_handler._db_util.db_mapping_calls[gbk_interface_name]

    def tearDown(self):
        None
    
    def _atleast_one(self,expectant,graph):
        for triple in graph:
            for element in triple:
                if str(expectant) in str(element):
                    return True
                if str(expectant) == str(element):
                    return True
        return False

    def test_genbank_interface_get_id(self):
        gbk_id = "AY150213.1"
        record = self.gbk_interface.get(gbk_id)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(gbk_id,record))
        
    def test_genbank_interface_get_uri(self):
        gbk_uri = URIRef("https://www.ncbi.nlm.nih.gov/nuccore/KJ775863.1")
        record = self.gbk_interface.get(gbk_uri)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one("KJ775863.1",record))

    def test_genbank_interface_get_id_no_record(self):
        self.assertRaises(ValueError, self.gbk_interface.get,"BBa_K16530044")

    def test_genbank_interface_get_uri_no_record(self):
        gbk_uri = URIRef("https://www.ncbi.nlm.nih.gov/nuccore/KJ77586333.1")
        self.assertRaises(ValueError, self.gbk_interface.get,gbk_uri)
        gbk_uri = URIRef("https://synbiohub.org/public/bsu/module_BO_30843_encodes_BO_112399/1")
        self.assertRaises(ValueError, self.gbk_interface.get,gbk_uri)

    def test_genbank_interface_query_match_single(self):
        query_strings = ["laci","ptetr","pbad","gfp"]
        for query_string in query_strings:
            results = self.gbk_interface.query(query_string)
            self.assertIsInstance(results,list)
            self.assertGreater(len(results),0)

    def test_genbank_interface_query_match_multiple(self):
        query_strings = ["laci repressor","autoinducer synthetase" ,"inducible promoter","gfp fluorescence"]
        for query_string in query_strings:
            results = self.gbk_interface.query(query_string)
            self.assertIsInstance(results,list)
            self.assertGreater(len(results),0)

    def test_genbank_interface_query_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_query_match"]
        for query_string in query_strings:
            results = self.gbk_interface.query(query_string)
            self.assertIsInstance(results,list)
            self.assertEqual(len(results),0)

    def test_genbank_interface_query_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            results = self.gbk_interface.query(query_string)
            self.assertIsInstance(results,list)
            self.assertEqual(len(results),0,query_string)

    def test_genbank_interface_count_match_single(self):
        query_strings = ["laci","ptetr","pbad","gfp"]
        for query_string in query_strings:
            count = self.gbk_interface.count(query_string)
            self.assertGreater(count,0)

    def test_genbank_interface_count_match_multiple(self):
        query_strings = ["laci repressor","autoinducer synthetase" ,"inducible promoter","gfp fluorescence"]
        for query_string in query_strings:
            count = self.gbk_interface.count(query_string)
            self.assertGreater(count,0)

    def test_genbank_interface_count_no_match_single(self):
        query_strings = ["no_match_here","atvg","random_word","no_query_match"]
        for query_string in query_strings:
            count = self.gbk_interface.count(query_string)
            self.assertEqual(count,0)

    def test_genbank_interface_count_no_match_multiple(self):
        query_strings = ["laci no_match_here","ptetr repressible atvg","pbad random_word","gfp no_match"]
        for query_string in query_strings:
            count = self.gbk_interface.count(query_string)
            self.assertEqual(count,0)


class TestDatabaseHandlerVPR(unittest.TestCase):
    def setUp(self):
        self.db_handler = DatabaseHandler()
        vpr_interface_name = self.db_handler.vpr
        self.vpr_interface = self.db_handler._db_util.db_mapping_calls[vpr_interface_name]

    def tearDown(self):
        None
    
    def _atleast_one(self,expectant,graph):
        for triple in graph:
            for element in triple:
                if str(expectant) in str(element):
                    return True
                if str(expectant) == str(element):
                    return True
        return False
    
    def _equal_graphs(self,g1,g2):
        self.assertCountEqual([*g1.triples((None,None,None))],
                              [*g2.triples((None,None,None))])

    def test_vpr_get(self):
        vpr_id = "BO_31362"
        record = self.vpr_interface.get(vpr_id)
        self.assertIsInstance(record,Graph)
        self.assertGreater(len(record),0)
        self.assertTrue(self._atleast_one(vpr_id,record))

        vpr_id = "http://www.bacillondex.org/BO_31362/1"
        record1 = self.vpr_interface.get(vpr_id)
        self.assertIsInstance(record1,Graph)
        self.assertGreater(len(record1),0)
        self.assertTrue(self._atleast_one(vpr_id,record))
        self._equal_graphs(record,record1)
        
    def test_vpr_query(self):
        query_strings = ["ylaA"]
        for query_string in query_strings:
            results = self.vpr_interface.query(query_string)
            self.assertGreater(len(results),0)

    def test_vpr_count(self):
        query_strings = ["ylaA"]
        for query_string in query_strings:
            results = self.vpr_interface.count(query_string)
            self.assertGreater(results,0)

    def test_vpr_get_uri(self):
        name = "BO_31362"
        res = self.vpr_interface.get_uri(name)
        for r in res:
            if any(name in s for s in r):
                break
        else:
            self.fail()

    def test_vpr_is_triple(self):
        res = self.vpr_interface.is_triple("http://www.bacillondex.org/BO_31362/1")
        self.assertTrue(res)

    def test_vpr_sequence(self):
        res = self.vpr_interface.sequence("TGTTTCATCTTGAAACTTTTTGAAAAGTCCGCTGTCTAACCGAATGAGGCCTTAA")
        self.assertGreater(res,0)

if __name__ == '__main__':
    unittest.main()

