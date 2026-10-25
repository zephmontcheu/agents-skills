package ledger

// Entry is a double-entry ledger line. Amounts are int64 cents.
type Entry struct {
	ID     int64
	Debit  string
	Credit string
	Cents  int64
}

func Serve(addr string) {}
