from pathlib import Path

this_dir = Path(__file__).parent

dev = this_dir / 'env/dev.env'
stage = this_dir / 'env/stage.env'
prod = this_dir / 'env/prod.env'
