from src.paths import PROJECT_ROOT
import src.run_pipeline

def test_run_pipeline_import():
    assert hasattr(src.run_pipeline, "main")
    assert PROJECT_ROOT.exists()
