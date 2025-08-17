import {
  DataTable,
  Table,
  TableHead,
  TableRow,
  TableHeader,
  TableBody,
  TableCell,
  Button,
} from '@carbon/react';
import { View } from '@carbon/icons-react';
import { useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { cryptoAnalyticsApi } from '../api';
import { useAlert } from '../contexts/AlertContext.jsx';
import './CryptoTable.scss';

function CryptoTable() {
  const navigate = useNavigate();
  const { success, error: showError } = useAlert();
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSymbols = async () => {
      try {
        setLoading(true);
        const data = await cryptoAnalyticsApi.getAllSymbolsSummary();
        setSymbols(data.symbols || []);
        success(`Successfully loaded ${data.symbols?.length || 0} crypto symbols`);
      } catch (err) {
        console.error('Error fetching symbols:', err);
        setError(err.message);
        showError('Failed to load crypto data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSymbols();
  }, [success, showError]);

  const headers = [
    { key: 'symbol', header: 'Symbol' },
    { key: 'current_price', header: 'Current Price' },
    { key: 'daily_change_percent', header: 'Daily Change' },
    { key: 'daily_avg', header: 'Daily Avg' },
  ];

  const rows = symbols.map((symbol) => ({
    id: symbol.symbol.toLowerCase().replace('usdt', ''),
    symbol: symbol.symbol.replace('USDT', ''),
    current_price: `$${symbol.current_price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
    daily_change_percent: `${symbol.daily_change_percent > 0 ? '+' : ''}${symbol.daily_change_percent.toFixed(2)}%`,
    daily_avg: `$${symbol.daily_avg.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
  }));

  const handleView = (id) => {
    navigate(`/coin/${id}`);
  };

  const getChangeColorStyle = (change) => {
    const changeValue = parseFloat(change.replace('%', '').replace('+', ''));
    if (changeValue > 0) return { color: '#297854', fontWeight: 'bold' };
    if (changeValue < 0) return { color: '#b51633', fontWeight: 'bold' };
    return { color: '#8a6b27', fontWeight: 'bold' };
  };

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '200px',
        color: 'white'
      }}>
        <div>Loading crypto data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '200px',
        color: '#b51633'
      }}>
        <div>Error loading data: {error}</div>
      </div>
    );
  }

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
        <Table {...getTableProps()} className="crypto-table">
          <TableHead>
            <TableRow>
              {headers.map((header) => (
                <TableHeader key={header.key} {...getHeaderProps({ header })}>
                  {header.header}
                </TableHeader>
              ))}
              <TableHeader>Actions</TableHeader>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map((row) => (
              <TableRow key={row.id} {...getRowProps({ row })}>
                {row.cells.map((cell) => (
                  <TableCell
                    key={cell.id}
                    style={
                      cell.info.header === 'daily_change_percent'
                        ? getChangeColorStyle(cell.value)
                        : undefined
                    }
                  >
                    {cell.value}
                  </TableCell>
                ))}
                <TableCell>
                  <Button
                    renderIcon={View}
                    kind="ghost"
                    size="sm"
                    iconDescription="View Coin"
                    onClick={() => handleView(row.id)}
                  />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </DataTable>
  );
}

export default CryptoTable;