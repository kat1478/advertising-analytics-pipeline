from src.paths import PROJECT_ROOT
import src.run_pipeline

def test_run_pipeline_import():
    assert hasattr(src.run_pipeline, "run_pipeline"), (
        "src.run_pipeline must expose a callable 'run_pipeline' function"
    )
    assert callable(src.run_pipeline.run_pipeline)
    assert PROJECT_ROOT.exists()
