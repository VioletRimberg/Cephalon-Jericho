from pydantic import BaseModel
from logging import error, info
from pathlib import Path

JERICHO_STATE_FILE = Path("state.json")

class State(BaseModel):
    # How many times Jericho has been "reset"
    deathcounter: int = 0

    @classmethod
    def load(cls)->"State":
        """
        Load the state from the state file.
        """
        if JERICHO_STATE_FILE.exists():
            with open(JERICHO_STATE_FILE, "r") as f:
                try:
                    state = cls.parse_raw(f.read())
                    return state
                except Exception as e:
                    error(f"Error reading Jericho state file: {e}. Creating new state.")

        new_state = cls()
        new_state.save()
        return cls()

    def save(self):
        """
        Save the state to the state file.
        """
        with open(JERICHO_STATE_FILE, "w") as f:
            f.write(self.model_dump_json(indent=4))
            info("Created new state file.")
