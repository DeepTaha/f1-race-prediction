"""
F1 Data Loader
Loads real historical data via FastF1 (cached to parquet) with a synthetic fallback.

FastF1 v3.x no longer returns Position/GridPosition/Status/Points from Ergast
(deprecated Nov 2024). We derive all result fields from lap timing data:
  - finish_position: ranked by laps completed DESC then cumulative time ASC
  - grid_position:   GridPosition col -> Q1/Q2/Q3 times -> lap-1 position -> default
  - dnf:             fewer laps than race winner AND no recorded finish time
  - points:          standard F1 table applied to derived finish_position
"""

import os
import pandas as pd
import numpy as np

try:
    import fastf1
    FASTF1_AVAILABLE = True
except ImportError:
    FASTF1_AVAILABLE = False

# Standard F1 points awarded to positions 1-10
_F1_POINTS: dict[int, float] = {
    1: 25.0, 2: 18.0, 3: 15.0, 4: 12.0, 5: 10.0,
    6:  8.0, 7:  6.0, 8:  4.0, 9:  2.0, 10:  1.0,
}

# Canonical team name mapping — normalises historical name changes so the
# label encoder sees a stable set of team identities across all seasons.
_TEAM_NAMES: dict[str, str] = {
    # Red Bull
    "Red Bull Racing": "Red Bull",
    "Oracle Red Bull Racing": "Red Bull",
    "Red Bull Racing Honda RBPT": "Red Bull",
    # Mercedes
    "Mercedes": "Mercedes",
    "Mercedes-AMG Petronas F1 Team": "Mercedes",
    "Mercedes-AMG Petronas Formula One Team": "Mercedes",
    # Ferrari
    "Ferrari": "Ferrari",
    "Scuderia Ferrari": "Ferrari",
    "Scuderia Ferrari HP": "Ferrari",
    # McLaren
    "McLaren": "McLaren",
    "McLaren F1 Team": "McLaren",
    "McLaren Mercedes": "McLaren",
    # Aston Martin lineage (Racing Point / Force India)
    "Aston Martin": "Aston Martin",
    "Aston Martin F1 Team": "Aston Martin",
    "Aston Martin Aramco F1 Team": "Aston Martin",
    "Aston Martin Aramco Cognizant F1 Team": "Aston Martin",
    "Racing Point": "Aston Martin",
    "BWT Racing Point F1 Team": "Aston Martin",
    "Force India": "Aston Martin",
    # Alpine lineage (Renault)
    "Alpine": "Alpine",
    "Alpine F1 Team": "Alpine",
    "BWT Alpine F1 Team": "Alpine",
    "Renault": "Alpine",
    # Williams
    "Williams": "Williams",
    "Williams Racing": "Williams",
    # Haas
    "Haas": "Haas",
    "Haas F1 Team": "Haas",
    "MoneyGram Haas F1 Team": "Haas",
    # Sauber lineage (Alfa Romeo / Kick Sauber / Audi)
    "Alfa Romeo": "Sauber",
    "Alfa Romeo Racing": "Sauber",
    "Alfa Romeo F1 Team ORLEN": "Sauber",
    "Kick Sauber": "Sauber",
    "Stake F1 Team Kick Sauber": "Sauber",
    "Sauber": "Sauber",
    "Audi": "Sauber",
    "Audi F1 Team": "Sauber",
    # Red Bull junior team lineage (Toro Rosso -> AlphaTauri -> RB)
    "AlphaTauri": "RB",
    "Scuderia AlphaTauri": "RB",
    "Scuderia AlphaTauri Honda": "RB",
    "RB": "RB",
    "Racing Bulls": "RB",
    "Visa Cash App RB": "RB",
    "Visa Cash App RB Formula One Team": "RB",
    "Toro Rosso": "RB",
    "Scuderia Toro Rosso": "RB",
}


def _normalize_team(name: str) -> str:
    return _TEAM_NAMES.get(name, name)


def get_next_race(years_to_try: list[int] | None = None) -> dict | None:
    """
    Return metadata for the next upcoming race using FastF1's event schedule.
    Returns None if FastF1 is unavailable or no future race is found.
    """
    if not FASTF1_AVAILABLE:
        return None

    import pandas as pd
    today = pd.Timestamp.now(tz="UTC")

    for year in (years_to_try or [today.year, today.year + 1]):
        try:
            schedule = fastf1.get_event_schedule(year, include_testing=False).copy()
            schedule["_date"] = pd.to_datetime(schedule["EventDate"], utc=True)
            future = schedule[schedule["_date"] >= today].sort_values("_date")
            if len(future) == 0:
                continue
            event = future.iloc[0]
            track_name = str(event["EventName"]).replace(" Grand Prix", "").strip()
            return {
                "race": str(event["EventName"]),
                "circuit": str(event.get("Location", event["EventName"])),
                "season": int(year),
                "round": int(event["RoundNumber"]),
                "track": track_name,
                "weather": "Dry",
                "temperature": 25,
            }
        except Exception:
            continue
    return None


class F1DataLoader:
    """Load and prepare F1 race data — real via FastF1 or synthetic fallback."""

    def __init__(
        self,
        cache_dir: str = "dataset/fastf1_cache",
        data_path: str = "dataset/historical_data.parquet",
    ):
        self.cache_dir = cache_dir
        self.data_path = data_path
        self.results_df: pd.DataFrame | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def load_historical_data(
        self, years: list[int] | None = None, force_refresh: bool = False
    ) -> pd.DataFrame:
        """
        Load real F1 data.  On first call downloads via FastF1 and saves a
        parquet cache; subsequent calls return the cache instantly.
        Falls back to synthetic data if FastF1 is unavailable or fails.
        """
        if not force_refresh and os.path.exists(self.data_path):
            df = pd.read_parquet(self.data_path)
            print(f"[OK] Loaded {len(df)} race records from cache ({self.data_path})")
            self.results_df = df
            return df

        if not FASTF1_AVAILABLE:
            print("[WARN] FastF1 not installed -- using synthetic sample data")
            return self.load_sample_data()

        try:
            return self._fetch_from_fastf1(years or [2021, 2022, 2023, 2024])
        except Exception as exc:
            print(f"[WARN] FastF1 fetch failed ({exc}) -- falling back to synthetic data")
            return self.load_sample_data()

    # ------------------------------------------------------------------
    # FastF1 fetch
    # ------------------------------------------------------------------

    def _fetch_from_fastf1(self, years: list[int]) -> pd.DataFrame:
        """Download race results from the FastF1 API and persist to parquet."""
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(self.data_path)), exist_ok=True)
        fastf1.Cache.enable_cache(self.cache_dir)

        records: list[dict] = []

        for year in years:
            print(f"\n-> Loading {year} season...")
            try:
                schedule = fastf1.get_event_schedule(year, include_testing=False)
            except Exception as exc:
                print(f"  [WARN] Could not get {year} schedule: {exc}")
                continue

            for _, event in schedule.iterrows():
                round_num = int(event["RoundNumber"])
                event_name = str(event["EventName"])
                track_name = event_name.replace(" Grand Prix", "").strip()
                _safe_track = track_name.encode("ascii", "replace").decode()

                try:
                    session = fastf1.get_session(year, round_num, "R")
                    # laps=True is required: Position/GridPosition/Status are NaN in FastF1
                    # v3.x (Ergast deprecated). We derive all result fields from lap timing.
                    session.load(laps=True, telemetry=False, weather=True, messages=False)

                    # Weather summary
                    wd = session.weather_data
                    is_wet = (
                        bool(wd["Rainfall"].any())
                        if wd is not None and len(wd) > 0
                        else False
                    )
                    temp = (
                        float(wd["AirTemp"].mean())
                        if wd is not None and len(wd) > 0 and "AirTemp" in wd.columns
                        else 25.0
                    )

                    race_rows = self._build_race_rows(session)
                    if not race_rows:
                        print(f"  [WARN] {year} R{round_num:02d} ({_safe_track}): no lap data")
                        continue

                    for row in race_rows:
                        records.append({
                            "race_id": year * 100 + round_num,
                            "year": year,
                            "round": round_num,
                            "track": track_name,
                            **row,
                            "weather": "Wet" if is_wet else "Dry",
                            "temperature": max(10, min(50, round(temp))),
                        })

                    print(f"  [OK] {year} R{round_num:02d} - {_safe_track} ({len(race_rows)} drivers)")

                except Exception as exc:
                    print(f"  [WARN] {year} R{round_num:02d} ({_safe_track}): {exc}")
                    continue

        if not records:
            print("[WARN] No data fetched from FastF1 -- using synthetic data")
            return self.load_sample_data()

        df = pd.DataFrame(records)
        df.to_parquet(self.data_path, index=False)
        print(f"\n[OK] Saved {len(df)} records -> {self.data_path}")
        self.results_df = df
        return df

    # ------------------------------------------------------------------
    # Position derivation helpers (Ergast workaround)
    # ------------------------------------------------------------------

    def _build_race_rows(self, session) -> list[dict]:
        """
        Build per-driver result dicts using lap timing instead of results columns.

        Since FastF1 v3.x no longer populates Position/GridPosition/Points/Status
        (all sourced from deprecated Ergast), we reconstruct them from:
          - session.laps  -> finish position, laps completed, DNF flag
          - session.results Q1/Q2/Q3 cols OR lap-1 positions -> grid position
        """
        results = session.results
        if results is None or len(results) == 0:
            return []

        laps = session.laps

        # --- Step 1: laps completed + cumulative time per driver ---------------
        laps_completed: dict[str, int] = {}
        cum_times: dict[str, float] = {}

        if laps is not None and len(laps) > 0:
            # Fastest/last lap has the highest LapNumber per driver
            last = (
                laps.sort_values("LapNumber")
                .groupby("Driver")
                .last()
                .reset_index()
            )
            for _, row in last.iterrows():
                abbr = str(row["Driver"])
                laps_completed[abbr] = int(row["LapNumber"])
                cum_times[abbr] = self._timedelta_secs(row.get("Time"))

            # Also grab max lap count separately (in case last row isn't the final lap)
            max_per_driver = laps.groupby("Driver")["LapNumber"].max()
            for abbr, n in max_per_driver.items():
                laps_completed[str(abbr)] = int(n)

        # Fall back to Laps column in results if lap data is empty
        if not laps_completed:
            for _, r in results.iterrows():
                abbr = str(r.get("Abbreviation", ""))
                if abbr:
                    laps_completed[abbr] = self._safe_int(r.get("Laps"), default=0)
                    cum_times[abbr] = self._timedelta_secs(r.get("Time"))

        if not laps_completed or max(laps_completed.values(), default=0) == 0:
            return []

        max_race_laps = max(laps_completed.values())

        # --- Step 2: rank drivers -> finish positions --------------------------
        # All drivers in results (preserves metadata even if no lap data)
        all_abbrs = [
            str(a) for a in results["Abbreviation"].dropna().tolist()
            if str(a) not in ("nan", "")
        ]

        ranked_abbrs = sorted(
            all_abbrs,
            key=lambda d: (
                -laps_completed.get(d, 0),
                cum_times.get(d, float("inf")),
            ),
        )

        # --- Step 3: grid positions --------------------------------------------
        grid_positions = self._get_grid_positions(session, results, all_abbrs)

        # --- Step 4: fastest lap map ------------------------------------------
        fl_map: dict[str, int] = {}
        if "FastestLapRank" in results.columns:
            for _, r in results.iterrows():
                abbr = str(r.get("Abbreviation", ""))
                if abbr:
                    fl_map[abbr] = 1 if self._safe_int(r.get("FastestLapRank"), 99) == 1 else 0

        # --- Step 5: assemble rows --------------------------------------------
        results_idx = {
            str(r["Abbreviation"]): r
            for _, r in results.iterrows()
            if str(r.get("Abbreviation", "")) not in ("nan", "")
        }

        rows: list[dict] = []
        for finish_pos, abbr in enumerate(ranked_abbrs, start=1):
            r = results_idx.get(abbr)
            if r is None:
                continue

            driver_laps = laps_completed.get(abbr, 0)
            has_finish_time = cum_times.get(abbr, float("inf")) < float("inf")
            dnf = 1 if (driver_laps < max_race_laps and not has_finish_time) else 0

            rows.append({
                "driver": abbr,
                "driver_name": str(r.get("FullName", "")),
                "grid_position": grid_positions.get(abbr, 10),
                "finish_position": finish_pos,
                "points": _F1_POINTS.get(finish_pos, 0.0),
                "fastest_lap": fl_map.get(abbr, 0),
                "dnf": dnf,
                "team": _normalize_team(str(r.get("TeamName", "Unknown"))),
            })

        return rows

    def _get_grid_positions(
        self, session, results: pd.DataFrame, driver_abbrs: list[str]
    ) -> dict[str, int]:
        """
        Try multiple strategies to get grid starting positions.

        Priority:
          1. results.GridPosition (direct, but NaN when Ergast is down)
          2. Q1/Q2/Q3 qualifying times in results (derive ranking)
          3. Position at start of lap 1 from session.laps
          4. Sequential default (index order, midfield-biased)
        """
        grid_map: dict[str, int] = {}
        threshold = max(1, len(driver_abbrs) * 0.8)

        # Strategy 1: GridPosition column
        if "GridPosition" in results.columns:
            for _, r in results.iterrows():
                abbr = str(r.get("Abbreviation", ""))
                gp = self._safe_int(r.get("GridPosition"), default=0)
                if abbr and abbr not in ("nan", "") and gp > 0:
                    grid_map[abbr] = gp
            if len(grid_map) >= threshold:
                return self._fill_missing_grid(grid_map, driver_abbrs)

        # Strategy 2: Q time ranking
        q_map = self._grid_from_quali(results)
        if len(q_map) >= threshold:
            return self._fill_missing_grid(q_map, driver_abbrs)

        # Strategy 3: lap-1 positions from laps data
        try:
            laps = session.laps
            if laps is not None and len(laps) > 0:
                lap1 = laps[laps["LapNumber"] == 1]
                if "Position" in lap1.columns:
                    for _, row in lap1.iterrows():
                        abbr = str(row.get("Driver", ""))
                        pos = self._safe_int(row.get("Position"), default=0)
                        if abbr and pos > 0:
                            grid_map[abbr] = pos
                    if len(grid_map) >= threshold:
                        return self._fill_missing_grid(grid_map, driver_abbrs)
        except Exception:
            pass

        # Strategy 4: use Q map if partial, else default index
        if q_map:
            return self._fill_missing_grid(q_map, driver_abbrs)

        return self._fill_missing_grid(grid_map, driver_abbrs)

    def _fill_missing_grid(
        self, grid_map: dict[str, int], driver_abbrs: list[str]
    ) -> dict[str, int]:
        """Fill any drivers not in grid_map with sequential positions."""
        used = set(grid_map.values())
        next_pos = 1
        result = dict(grid_map)
        for abbr in driver_abbrs:
            if abbr not in result:
                while next_pos in used:
                    next_pos += 1
                result[abbr] = min(next_pos, 20)
                used.add(next_pos)
                next_pos += 1
        return result

    def _grid_from_quali(self, results: pd.DataFrame) -> dict[str, int]:
        """Derive grid positions from Q1/Q2/Q3 qualifying times in results."""
        entries: list[tuple[str, int, float]] = []

        for _, r in results.iterrows():
            abbr = str(r.get("Abbreviation", ""))
            if not abbr or abbr == "nan":
                continue
            q3 = self._timedelta_secs(r.get("Q3") if "Q3" in results.columns else None)
            q2 = self._timedelta_secs(r.get("Q2") if "Q2" in results.columns else None)
            q1 = self._timedelta_secs(r.get("Q1") if "Q1" in results.columns else None)

            if q3 < float("inf"):
                entries.append((abbr, 0, q3))
            elif q2 < float("inf"):
                entries.append((abbr, 1, q2))
            elif q1 < float("inf"):
                entries.append((abbr, 2, q1))
            else:
                entries.append((abbr, 3, float("inf")))

        if not entries:
            return {}

        sorted_entries = sorted(entries, key=lambda x: (x[1], x[2]))
        return {abbr: pos + 1 for pos, (abbr, _, _) in enumerate(sorted_entries)}

    # ------------------------------------------------------------------
    # Synthetic fallback
    # ------------------------------------------------------------------

    def load_sample_data(self) -> pd.DataFrame:
        """300-race synthetic dataset used when FastF1 is unavailable."""
        np.random.seed(42)
        drivers = ["VER", "HAM", "LEC", "NOR", "PIA", "SAI", "RUS", "ALO", "PER", "STR"]
        tracks = ["Abu Dhabi", "Monza", "Silverstone", "Monaco", "Spa"]
        teams = ["Red Bull", "Mercedes", "Ferrari", "McLaren", "Aston Martin"]

        data = [
            {
                "race_id": i,
                "year": np.random.choice([2021, 2022, 2023, 2024]),
                "round": (i % 22) + 1,
                "track": np.random.choice(tracks),
                "driver": np.random.choice(drivers),
                "driver_name": np.random.choice(drivers),
                "grid_position": np.random.randint(1, 21),
                "finish_position": np.random.randint(1, 21),
                "points": np.random.choice([25, 18, 15, 12, 10, 8, 6, 4, 2, 1, 0]),
                "fastest_lap": np.random.choice([0, 1], p=[0.9, 0.1]),
                "dnf": np.random.choice([0, 1], p=[0.85, 0.15]),
                "team": np.random.choice(teams),
                "weather": np.random.choice(["Dry", "Wet"], p=[0.8, 0.2]),
                "temperature": np.random.randint(20, 35),
            }
            for i in range(300)
        ]

        self.results_df = pd.DataFrame(data)
        print(f"[OK] Loaded {len(self.results_df)} synthetic race records (fallback)")
        return self.results_df

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _timedelta_secs(value) -> float:
        """Convert a timedelta / NaT / None to float seconds (inf if unavailable)."""
        try:
            return float(value.total_seconds())
        except (AttributeError, TypeError, ValueError):
            return float("inf")

    @staticmethod
    def _safe_int(value, default: int = 0) -> int:
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return default
