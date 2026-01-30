import pytest
import time
from argparse import Namespace
from app.aurorawatchuk_alerts import pre_checks, should_alert


# pre_checks() tests.
def test_pre_checks_valid_data():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    config = pre_checks(token, user, args)
    assert config == {
    "token": "abcdefghijklmnopqrstuvwxyz1234",
    "user": "abcdefghijklmnopqrstuvwxyz1234",
    "threshold": 1,
    "alert_interval": 3600,
    "check_interval": 300,
    "reduced_sensitivity": False,
    "ttl": 14400,
    }


def test_pre_checks_bad_token():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    # No token.
    token = None
    with pytest.raises(
        RuntimeError, match="PUSHOVER_APP_TOKEN environment variable missing."
    ):
        config = pre_checks(token, user, args)
    # Invalid token.
    token = "moo"
    with pytest.raises(
        ValueError, match="PUSHOVER_APP_TOKEN format not valid. Only a-z, 0-9, 30 characters."
    ):
        config = pre_checks(token, user, args)


def test_pre_checks_bad_user():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    # No user.
    user = None
    with pytest.raises(
        RuntimeError, match="PUSHOVER_USER_KEY environment variable missing."
    ):
        config = pre_checks(token, user, args)
    # Invalid token.
    user = "moo"
    with pytest.raises(
        ValueError, match="PUSHOVER_USER_KEY format not valid. Only a-z, 0-9, 30 characters."
    ):
        config = pre_checks(token, user, args)


def test_pre_checks_bad_threshold():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    # Threshold not an integer
    args.threshold = "moo"
    with pytest.raises(TypeError, match="Threshold must be an integer."):
        config = pre_checks(token, user, args)
    # Threshold out of range.
    args.threshold = 5
    with pytest.raises(ValueError, match="Threshold must be between 1 and 3."):
        config = pre_checks(token, user, args)


def test_pre_checks_bad_alert_interval():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    # Alert interval not an integer.
    args.alert_interval = "moo"
    with pytest.raises(TypeError, match="Alert interval must be an integer."):
        config = pre_checks(token, user, args)
    # Alert interval out of range.
    args.alert_interval = -1
    with pytest.raises(ValueError, match="Alert interval must be > 0."):
        config = pre_checks(token, user, args)


def test_pre_checks_bad_check_interval():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    # Check interval not an integer.
    args.check_interval = "moo"
    with pytest.raises(TypeError, match="Check interval must be an integer."):
        config = pre_checks(token, user, args)
    # Check interval out of range.
    args.check_interval = 100
    with pytest.raises(ValueError, match="Check interval must be >= 180."):
        config = pre_checks(token, user, args)


def test_pre_checks_bad_ttl():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )
    # TTL interval not an integer.
    args.ttl = "moo"
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


def test_pre_checks_bad_ttl():
    # Valid test data.
    token = "abcdefghijklmnopqrstuvwxyz1234"
    user = "abcdefghijklmnopqrstuvwxyz1234"
    args = Namespace(
        threshold=1,
        alert_interval=3600,
        check_interval=300,
        reduced_sensitivity=False,
        ttl=14400,
    )


# should_alert() tests.
def test_should_alert_invalid_current_status():
    # Valid data.
    config = {
    "token": "abcdefghijklmnopqrstuvwxyz1234",
    "user": "abcdefghijklmnopqrstuvwxyz1234",
    "threshold": 1,
    "alert_interval": 3600,
    "check_interval": 300,
    "reduced_sensitivity": False,
    "ttl": 14400,
    }
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    # Invalid current status
    state["current_status"] = None
    assert should_alert(config, state) == False


def test_should_alert_status_green_below_threshold_yellow():
    # Valid data.
    config = {
    "token": "abcdefghijklmnopqrstuvwxyz1234",
    "user": "abcdefghijklmnopqrstuvwxyz1234",
    "threshold": 1,
    "alert_interval": 3600,
    "check_interval": 300,
    "reduced_sensitivity": False,
    "ttl": 14400,
    }
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    # Current status green, threshold yellow.
    state["current_status"] = 0
    config["threshold"] = 1
    assert should_alert(config, state) == False
    # Check returned state is correct.
    assert state["current_status"] == 0
    
    
def test_should_alert_status_yellow_below_threshold_amber():
    # Valid data.
    config = {
    "token": "abcdefghijklmnopqrstuvwxyz1234",
    "user": "abcdefghijklmnopqrstuvwxyz1234",
    "threshold": 1,
    "alert_interval": 3600,
    "check_interval": 300,
    "reduced_sensitivity": False,
    "ttl": 14400,
    }
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    # Current status green, threshold yellow.
    state["current_status"] = 1
    config["threshold"] = 2
    assert should_alert(config, state) == False
    # Check returned state is correct.
    assert state["current_status"] == 1


def test_should_alert_status_amber_below_threshold_red():
    # Valid data.
    config = {
        "token": "abcdefghijklmnopqrstuvwxyz1234",
        "user": "abcdefghijklmnopqrstuvwxyz1234",
        "threshold": 1,
        "alert_interval": 3600,
        "check_interval": 300,
        "reduced_sensitivity": False,
        "ttl": 14400,
    }
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    # Current status green, threshold yellow.
    state["current_status"] = 2
    config["threshold"] = 3
    assert should_alert(config, state) == False
    # Check returned state is correct.
    assert state["current_status"] == 2


def test_should_alert_alertinterval():
    # Valid data.
    config = {
    "token": "abcdefghijklmnopqrstuvwxyz1234",
    "user": "abcdefghijklmnopqrstuvwxyz1234",
    "threshold": 1,
    "alert_interval": 3600,
    "check_interval": 300,
    "reduced_sensitivity": False,
    "ttl": 14400,
    }
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    # First time at threshold.
    now = 1
    state["current_status"] = 1
    assert should_alert(config, state, now) == True
    # Again, but too soon.
    now = 2
    assert should_alert(config, state, now) == False
    # Again, enough time has passed.
    now = 3601
    assert should_alert(config, state, now) == True


def test_should_alert_escalation():
    # Valid data.
    config = {
    "token": "abcdefghijklmnopqrstuvwxyz1234",
    "user": "abcdefghijklmnopqrstuvwxyz1234",
    "threshold": 1,
    "alert_interval": 3600,
    "check_interval": 300,
    "reduced_sensitivity": False,
    "ttl": 14400,
    }
    state = {
        "current_status": 0,
        "last_alert_status": 0,
        "last_alert_time": 0,
    }
    # First time at threshold.
    now = 1
    state["current_status"] = 1
    assert should_alert(config, state, now) == True
    # Again, but too soon.
    now = 2
    assert should_alert(config, state, now) == False
    # Again, status has escalated.
    now = 3
    state["current_status"] = 2
    assert should_alert(config, state, now) == True
    # Again, but too soon.
    now = 4
    assert should_alert(config, state, now) == False
    # Again, status has escalated.
    now = 5
    state["current_status"] = 3
    assert should_alert(config, state, now) == True
