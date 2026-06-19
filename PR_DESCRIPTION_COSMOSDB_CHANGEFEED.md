# Cosmos DB Change Feed Mode Support

## Summary

Updated Python Azure Functions library to support Cosmos DB change feed modes (`LatestVersion` and `AllVersionsAndDeletes`), aligning with Azure WebJobs Extensions upstream implementation.

## Changes

- **Type Definitions**: Added `CosmosDBChangeFeedMode` type hint in `_cosmosdb.py` supporting 'LatestVersion' | 'AllVersionsAndDeletes'
- **Module Documentation**: Updated `CosmosDBConverter` and `CosmosDBTriggerConverter` class docstrings to document change feed mode behavior
- **Public API**: Exported `CosmosDBChangeFeedMode` type from main `__init__.py` for public consumption
- **Tests**: Added 3 new unit tests validating change feed mode support:
  - `test_cosmosdb_change_feed_mode_latest_version_support`: Validates LatestVersion mode
  - `test_cosmosdb_change_feed_mode_all_versions_and_deletes_support`: Validates AllVersionsAndDeletes mode
  - `test_cosmosdb_change_feed_mode_type_available`: Verifies type availability in public API
- **Version Bump**: Updated from 1.26.0b3 to 1.26.0

## Files Modified

- `azure/functions/_cosmosdb.py`: Added `CosmosDBChangeFeedMode` type
- `azure/functions/cosmosdb.py`: Updated documentation, exported type
- `azure/functions/__init__.py`: Exported and documented `CosmosDBChangeFeedMode`
- `tests/test_cosmosdb.py`: Added change feed mode tests

## Alignment

This change mirrors the Node.js library v4.16.1 Cosmos DB updates, ensuring consistent change feed support across both runtimes.
