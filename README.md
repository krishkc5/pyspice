# pyspice

Vertical slice that generates an LTspice netlist with OpenAI, runs LTspice headless, parses `.raw`, and plots waveforms.

## Setup

1. Create a `.env` file in the repository root:

   ```
   OPENAI_API_KEY=your_openai_api_key
   # Optional override if LTspice is not discoverable from PATH:
   # LTSPICE_PATH=/Applications/LTspice.app/Contents/MacOS/LTspice
   ```

2. Install dependencies:

   ```
   python3 -m pip install -e '.[dev]'
   ```

3. Run prerequisite diagnostics:

   ```
   pyspice doctor
   ```
