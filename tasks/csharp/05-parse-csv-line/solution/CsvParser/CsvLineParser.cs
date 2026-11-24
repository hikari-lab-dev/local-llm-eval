namespace CsvParser;

public static class CsvLineParser
{
    /// <summary>
    /// CSVの1行をフィールドのリストに分割する。
    /// </summary>
    public static List<string> ParseLine(string line)
    {
        return new LineParser(line).Parse();
    }

    private sealed class LineParser(string line)
    {
        private readonly List<string> _fields = [];
        private readonly System.Text.StringBuilder _current = new();
        private bool _inQuotes;
        private int _position;

        public List<string> Parse()
        {
            while (_position < line.Length)
            {
                ConsumeNextChar();
            }

            _fields.Add(_current.ToString());
            return _fields;
        }

        private void ConsumeNextChar()
        {
            var c = line[_position];
            if (_inQuotes)
            {
                ConsumeQuotedChar(c);
                return;
            }

            ConsumeUnquotedChar(c);
        }

        private void ConsumeQuotedChar(char c)
        {
            if (c != '"')
            {
                _current.Append(c);
                _position++;
                return;
            }

            if (HasEscapedQuoteAhead())
            {
                _current.Append('"');
                _position += 2;
                return;
            }

            _inQuotes = false;
            _position++;
        }

        private bool HasEscapedQuoteAhead()
        {
            var nextIndex = _position + 1;
            return nextIndex < line.Length && line[nextIndex] == '"';
        }

        private void ConsumeUnquotedChar(char c)
        {
            if (c == '"' && _current.Length == 0)
            {
                _inQuotes = true;
                _position++;
                return;
            }

            if (c == ',')
            {
                _fields.Add(_current.ToString());
                _current.Clear();
                _position++;
                return;
            }

            _current.Append(c);
            _position++;
        }
    }
}
