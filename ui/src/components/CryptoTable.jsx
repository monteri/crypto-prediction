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
import { Edit, TrashCan } from '@carbon/icons-react';

function CryptoTable() {
  const rows = [
    { id: 'a', name: 'Load balancer 1', status: 'Disabled' },
    { id: 'b', name: 'Load balancer 2', status: 'Starting' },
    { id: 'c', name: 'Load balancer 3', status: 'Active' },
  ];
  const headers = [
    { key: 'name',   header: 'Name'   },
    { key: 'status', header: 'Status' },
    { key: 'actions', header: 'Actions' },
  ];

  const handleEdit = id => { /* ... */ };
  const handleDelete = id => { /* ... */ };

  return (
    <DataTable rows={rows} headers={headers}>
      {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
        <Table {...getTableProps()}>
          <TableHead>
            <TableRow>
              {headers.map(header => (
                <TableHeader {...getHeaderProps({ header })}>
                  {header.header}
                </TableHeader>
              ))}
              <TableHeader>Actions</TableHeader>
            </TableRow>
          </TableHead>
          <TableBody>
            {rows.map(row => (
              <TableRow {...getRowProps({ row })}>
                {row.cells.map(cell => (
                  <TableCell key={cell.id}>{cell.value}</TableCell>
                ))}
                <TableCell>
                  {/* Inline buttons */}
                  <Button
                    renderIcon={Edit}
                    kind="ghost"
                    size="sm"
                    iconDescription="Edit"
                    onClick={() => handleEdit(row.id)}
                  />
                  <Button
                    renderIcon={TrashCan}
                    kind="ghost"
                    size="sm"
                    iconDescription="Delete"
                    onClick={() => handleDelete(row.id)}
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
