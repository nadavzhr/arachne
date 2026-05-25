"""Service for managing search profiles."""

from __future__ import annotations

from pathlib import Path

import yaml

from arachne.config.profile import SearchProfile, load_profile


class ProfileService:
    """Service to handle profile lifecycle (load, save, list)."""

    def __init__(self, profiles_dir: Path) -> None:
        """Initialize the profile service.

        Args:
            profiles_dir: Path to the directory where profiles are stored.
        """
        self.profiles_dir = profiles_dir

    def list_profiles(self) -> list[str]:
        """List all available profile names.

        Returns:
            list[str]: Sorted list of profile names (stems of .yaml files).
        """
        if not self.profiles_dir.exists():
            return []
        return sorted([f.stem for f in self.profiles_dir.glob("*.yaml")])

    def get_profile(self, name: str) -> SearchProfile:
        """Load a profile by name.

        Args:
            name: Name of the profile to load.

        Returns:
            SearchProfile: The loaded search profile.

        Raises:
            FileNotFoundError: If the profile file does not exist.
        """
        path = self.profiles_dir / f"{name}.yaml"
        if not path.exists():
            # Fallback for 'default' if it doesn't exist on disk but we want a blank one
            if name == "default":
                return SearchProfile(name="default")
            raise FileNotFoundError(f"Profile '{name}' not found at {path}")
        return load_profile(path)

    def save_profile(self, profile: SearchProfile) -> None:
        """Save a profile back to disk.

        Args:
            profile: The search profile instance to save.
        """
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        path = self.profiles_dir / f"{profile.name}.yaml"

        # Dump using Pydantic, excluding unset fields to keep the YAML clean
        data = profile.model_dump(mode="json", exclude_unset=True)

        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
