# QuranEnc Database Status

## Current Database Files

### Main Database (RECOMMENDED)
- **`quranenc_main.db`** - 104KB
  - ✅ Clean schema-based database
  - ✅ CRUD operations implemented
  - ✅ No duplicate metadata
  - ✅ Proper foreign key constraints
  - ✅ Verses table removed
  - ✅ One-to-many relationships (translations → files)

### Legacy Database (LOCKED)
- **`quranenc.db`** - 153MB
  - ⚠️ Contains corrupted metadata with duplicates
  - ⚠️ File locked by system process
  - ❌ Not recommended for use

## Backup Files (in `backup-dbs/`)

### Stable Backups
- **`quranenc_backup_20250901_104852.db`** - Last known good state
- **`quranenc_backup_20250901_104907.db`** - Intermediate backup
- **`quranenc_backup_safe_20250901_105002.db`** - Pre-restructure backup

### Corrupted/Intermediate Files
- **`quranenc_corrupted_20250901_113410.db`** - First corruption backup
- **`quranenc_corrupted_20250901_113441.db`** - Second corruption backup
- **`quranenc_locked_original.db`** - Copy of locked original
- **`quranenc_new_20250901_113441.db`** - Schema-recreated version (104KB)

## Archived Scripts (in `scripts-archive/`)
- Database analysis and fixing scripts
- Backup verification tools
- Schema recreation utilities
- CRUD implementation helpers

## Recommendations

1. **Use `quranenc_main.db`** as your primary database
2. Keep backups in `backup-dbs/` for safety
3. The locked `quranenc.db` can be removed when the process releases it
4. All database operations should now use CRUD-based approach

## Database Structure (quranenc_main.db)

### Tables:
- **translations** (68 records) - Translation metadata
- **files** (141 records) - Associated files with proper relationships
- **metadata** (9 records) - System metadata without duplicates
- **sqlite_sequence** - Auto-increment tracking

### Key Features:
- ✅ Foreign key constraints with CASCADE operations
- ✅ Proper indexes for performance
- ✅ UNIQUE constraints prevent duplicates
- ✅ Schema-driven design
- ✅ 90% size reduction (153MB → 104KB)