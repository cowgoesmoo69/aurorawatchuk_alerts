import pytest
import time
from argparse import Namespace
from app.aurorawatchuk_alerts import pre_checks, should_alert


# pre_checks() tests
def test_pre_checks():
    # Variables for tests.
    token = None
    user = None
    # Create a set of ArgumentParser args.
    args = Namespace(
        threshold="bad",
        alert_interval="bad",
        check_interval="bad",
        reduced_sensitivity=False,  # won't be tested as argparse controls True/False state.
        ttl="bad",
    )

    # No token.
    with pytest.raises(
        RuntimeError, match="PUSHOVER_APP_TOKEN environment variable missing."
    ):
        config = pre_checks(token, user, args)
    # Set a token, make it carry on.
    token = "moo"

    # No user.
    with pytest.raises(
        RuntimeError, match="PUSHOVER_USER_KEY environment variable missing."
    ):
        config = pre_checks(token, user, args)
    # Set a user, make it carry on.
    user = "moo"

    # Threshold not an integer.
    with pytest.raises(TypeError, match="Threshold must be an integer."):
        config = pre_checks(token, user, args)
    # Threshold out of range.
    args.threshold = 5
    with pytest.raises(ValueError, match="Threshold must be between 1 and 3."):
        config = pre_checks(token, user, args)
    # Set valid threshold, make it carry on.
    args.threshold = 3

    # Alert interval not an integer.
    with pytest.raises(TypeError, match="Alert interval must be an integer."):
        config = pre_checks(token, user, args)
    # Alert interval out of range.
    args.alert_interval = -1
    with pytest.raises(ValueError, match="Alert interval must be > 0."):
        config = pre_checks(token, user, args)
    # Set valid alert interval, make it carry on.
    args.alert_interval = 3600

    # Check interval not an integer.
    with pytest.raises(TypeError, match="Check interval must be an integer."):
        config = pre_checks(token, user, args)
    # Check interval out of range.
    args.check_interval = 100
    with pytest.raises(ValueError, match="Check interval must be >= 180."):
        config = pre_checks(token, user, args)
    # Set valid check interval, make it carry on.
    args.check_interval = 300

    # TTL interval not an integer.
    with pytest.raises(TypeError, match="TTL must be an integer."):
        config = pre_checks(token, user, args)
    # TTL out of range.
    args.ttl = 0
    with pytest.raises(ValueError, match="TTL must be betwen 1 and 31536000."):
        config = pre_checks(token, user, args)
    # TTL out of range.
    args.ttl = 31536001
    with pytest.raises(ValueError, match="TTL must be betwen 1 and 31536000."):
        config = pre_checks(token, user, args)
    # Set valid TTL, make it carry on.
    args.ttl = 14400

    # Check returned dict. Can use for
    config = pre_checks(token, user, args)
    assert config == {
        "token": "moo",
        "user": "moo",
        "threshold": 3,
        "alert_interval": 3600,
        "check_interval": 300,
        "reduced_sensitivity": False,
        "ttl": 14400,
    }


def test_should_alert():
    # Only need partial dict for testing.
    config = {
        "threshold": 2,
        "alert_interval": 3600,
    }
    # State dict for testing.
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }

    # Invalid current state
    state["current_status"] = None
    assert should_alert(config, state) == False

    # Valid current state, below threshold.
    state["current_status"] = 1
    state.update(
        {
            "last_alert_time": None,
            "last_alert_status": None,
        }
    )
    assert should_alert(config, state) == False
    # Check state is updated too.
    assert state == {
        "current_status": 1,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }

    # Interval timing
    state["current_status"] = 2
    assert should_alert(config, state) == True
    # Check state is updated too.
    assert state["last_alert_status"] == state["current_status"]
    assert state["last_alert_time"] > 0
    # Wait a second, then test again. Too soon.
    time.sleep(2)
    assert should_alert(config, state) == False
    # Manipulate the last alert time to emulate passage of two hours
    state["last_alert_time"] -= 7200
    # Test again.
    assert should_alert(config, state) == True

    # Escalating status overriding alert_interval.
    # First time meeting threshold.
    config = {
        "threshold": 1,
        "alert_interval": 3600,
    }
    # State dict for testing.
    state = {
        "current_status": 1,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    assert should_alert(config, state) == True
    # Wait, test again, too soon.
    time.sleep(2)
    assert should_alert(config, state) == False

    # Escalate to next level.
    state["current_status"] = 2
    assert should_alert(config, state) == True
    assert state["last_alert_status"] == 2
    # Wait, test again, too soon.
    time.sleep(2)
    assert should_alert(config, state) == False

    # Escalate to next level.
    state["current_status"] = 3
    assert should_alert(config, state) == True
    assert state["last_alert_status"] == 3
    # Wait, test again, too soon.
    time.sleep(2)
    assert should_alert(config, state) == False
