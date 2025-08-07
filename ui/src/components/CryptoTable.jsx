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
import './CryptoTable.scss';

function CryptoTable() {
  const navigate = useNavigate();

  // Memoize the data to prevent unnecessary re-renders
  const rows = [
    {
      id: 'bitcoin',
      name: 'BTC',
      currentValue: '124440.94$',
      dailyChange: '2.4%',
    },
    {
      id: 'ethereum',
      name: 'ETH',
      currentValue: '8324.15$',
      dailyChange: '-1.2%',
    },
    {
      id: 'solana',
      name: 'SOL',
      currentValue: '195.00$',
      dailyChange: '0.0%',
    },
  ];

  const headers = [
    { key: 'name', header: 'Name' },
    { key: 'currentValue', header: 'Current Value' },
    { key: 'dailyChange', header: 'Daily Change' },
  ];

  const handleView = (id) => {
    navigate(`/coin/${id}`);
  };

  const getChangeColorStyle = (change) => {
    let styles = { color: '#297854', fontWeight: 'bold' };
    if (change.startsWith('-')) styles = { color: '#b51633', fontWeight: 'bold' };
    if (change === '0.0%') styles = { color: '#8a6b27', fontWeight: 'bold' }
    return styles;
  };

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
                      cell.info.header === 'dailyChange'
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