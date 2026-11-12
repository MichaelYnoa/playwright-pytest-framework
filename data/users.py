"""Demo accounts published by saucedemo.com on its login page."""

from dataclasses import dataclass

PASSWORD = "secret_sauce"


@dataclass(frozen=True)
class User:
    username: str
    password: str = PASSWORD


STANDARD = User("standard_user")
LOCKED_OUT = User("locked_out_user")
PROBLEM = User("problem_user")
PERFORMANCE_GLITCH = User("performance_glitch_user")
VISUAL = User("visual_user")
INVALID = User("not_a_user", "wrong_password")
