from pandas import DataFrame

from app import SCHEMA, generate_dataframe, main


def test_main():
    # Simple does it run test
    main()


def test_generate_dataframe_has_schema_columns():
    # Test that a dataframe with at least the required columns according to schema is generated
    data = {"1234": "56789"}
    result = generate_dataframe(data)

    assert isinstance(result, DataFrame)
    assert all(col in [*result.columns] for col in [*SCHEMA.columns])
