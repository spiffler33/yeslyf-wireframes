// yeslyf board write-back (phase 11, Vatsal, 16 Sep 2026). Fill both values from the Supabase dashboard
// (Project settings, API): the project URL and the publishable (anon) key. Blank keeps every page local only
// (the top bar pill reads "offline, saved locally"). This file is served with the site and read by every page;
// the key is the public client key, not a secret; the board_entries policies allow insert and select only.
// build_site.py creates this file once when it is missing and never overwrites it.
var SUPABASE_URL = "";
var SUPABASE_ANON_KEY = "";
