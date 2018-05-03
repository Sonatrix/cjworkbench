from integrationtests.utils import LoggedInIntegrationTest

class TestLessons(LoggedInIntegrationTest):
    def test_lesson(self):
        b = self.browser
        b.visit(self.live_server_url + '/lessons/')
        b.find_by_xpath('//button[text()="Begin"]').click()

        self.assertTrue(b.url.endswith('/lessons/load-public-data/'))
        self.assertTrue(b.is_text_present('DROP MODULE HERE'))
        self.assertTrue(b.is_text_present('1. Load Public Data by URL'))
