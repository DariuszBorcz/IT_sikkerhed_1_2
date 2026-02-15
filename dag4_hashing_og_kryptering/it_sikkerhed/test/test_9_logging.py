import pytest
from src.logger.logger import LOGGER

#pytestmark = pytest.mark.focus

def test_logging_creates_expected_entries(tmp_path):
    # given 
    LOGGER.clean_log()

    # when
    LOGGER.info("Applikationen starter")
    LOGGER.error("Advarsel", extra={"http_error_code": 400})
    LOGGER.error("Noget gik galt", extra={"http_error_code": 500})

    # then
    log_data = LOGGER.read_file()

    print(f"\n{log_data}")

    assert "Applikationen starter" in log_data
    assert "Advarsel" in log_data
    assert "Noget gik galt" in log_data



