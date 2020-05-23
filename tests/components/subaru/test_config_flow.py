"""
Test the Subaru config flow.

Borrowed heavily from Tesla tests (thanks @alandtse)
"""
from datetime import datetime

from subarulink.exceptions import SubaruException

from homeassistant import config_entries, setup
from homeassistant.components.subaru.const import (
    CONF_HARD_POLL_INTERVAL,
    DEFAULT_HARD_POLL_INTERVAL,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MIN_HARD_POLL_INTERVAL,
    MIN_SCAN_INTERVAL,
)
from homeassistant.const import (
    CONF_DEVICE_ID,
    CONF_PASSWORD,
    CONF_PIN,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)

from tests.async_mock import patch
from tests.common import MockConfigEntry

TEST_USERNAME = "test@fake.com"
TEST_TITLE = TEST_USERNAME
TEST_PASSWORD = "test-password"
TEST_PIN = "1234"


async def test_form(hass):
    """Test we get the form."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == "form"
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.subaru.config_flow.SubaruAPI.connect",
        return_value=True,
    ) as mock_setup_entry:
        device_id = int(datetime.now().timestamp())
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: TEST_USERNAME,
                CONF_PASSWORD: TEST_PASSWORD,
                CONF_PIN: TEST_PIN,
            },
        )

    assert result2["type"] == "create_entry"
    assert result2["title"] == TEST_TITLE
    assert result2["data"][CONF_USERNAME] == TEST_USERNAME
    assert result2["data"][CONF_PASSWORD] == TEST_PASSWORD
    assert result2["data"][CONF_PIN] == TEST_PIN
    assert result2["data"][CONF_DEVICE_ID] == device_id

    await hass.async_block_till_done()
    assert len(mock_setup_entry.mock_calls) == 2


async def test_form_invalid_auth(hass):
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.subaru.config_flow.SubaruAPI.connect",
        side_effect=SubaruException("invalidAccount"),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: TEST_USERNAME,
                CONF_PASSWORD: TEST_PASSWORD,
                CONF_PIN: TEST_PIN,
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "invalid_credentials"}


async def test_form_cannot_connect(hass):
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.subaru.config_flow.SubaruAPI.connect",
        side_effect=SubaruException(None),
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: TEST_USERNAME,
                CONF_PASSWORD: TEST_PASSWORD,
                CONF_PIN: TEST_PIN,
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "connection_error"}


async def test_form_repeat_identifier(hass):
    """Test we handle repeat identifiers."""
    entry = MockConfigEntry(domain=DOMAIN, title=TEST_USERNAME, data={}, options=None)
    entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.subaru.config_flow.SubaruAPI.connect",
        return_value=True,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: TEST_USERNAME,
                CONF_PASSWORD: TEST_PASSWORD,
                CONF_PIN: TEST_PIN,
            },
        )

    assert result2["type"] == "form"
    assert result2["errors"] == {"base": "identifier_exists"}


async def test_option_flow(hass):
    """Test config flow options."""
    entry = MockConfigEntry(domain=DOMAIN, data={}, options=None)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: 350, CONF_HARD_POLL_INTERVAL: 3600},
    )
    assert result["type"] == "create_entry"
    assert result["data"] == {CONF_SCAN_INTERVAL: 350, CONF_HARD_POLL_INTERVAL: 3600}


async def test_option_flow_defaults(hass):
    """Test config flow options."""
    entry = MockConfigEntry(domain=DOMAIN, data={}, options=None)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], user_input={}
    )
    assert result["type"] == "create_entry"
    assert result["data"] == {
        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
        CONF_HARD_POLL_INTERVAL: DEFAULT_HARD_POLL_INTERVAL,
    }


async def test_option_flow_input_floor(hass):
    """Test config flow options."""
    entry = MockConfigEntry(domain=DOMAIN, data={}, options=None)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] == "form"
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={CONF_SCAN_INTERVAL: 1, CONF_HARD_POLL_INTERVAL: 1},
    )
    assert result["type"] == "create_entry"
    assert result["data"] == {
        CONF_SCAN_INTERVAL: MIN_SCAN_INTERVAL,
        CONF_HARD_POLL_INTERVAL: MIN_HARD_POLL_INTERVAL,
    }
