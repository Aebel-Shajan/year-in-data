import { MaterialReactTable, MRT_ColumnDef, useMaterialReactTable } from "material-react-table";
import { useMemo } from "react";
import {GithubActivity} from "../ManageData"


const TableView = ({data}: {data: GithubActivity[]}) => {
    //column definitions - strongly typed if you are using TypeScript (optional, but recommended)
    const columns = useMemo<MRT_ColumnDef<GithubActivity>[]>(
      () => [
        {
          accessorKey: 'date', 
          header: 'Date',
        },
        {
          accessorKey: 'repository_image',
          header: 'Image',
        },
        {
          accessorKey: 'repository_name',
          header: 'repository_name'
        },
        {
          accessorKey: 'repository_url',
          header: 'repository_url'
        },
        {
          accessorKey: 'total_commits',
          header: 'total_commits'
        }
      ],
      [],
    );
  
    //pass table options to useMaterialReactTable
    const table = useMaterialReactTable({
      columns,
      data, //must be memoized or stable (useState, useMemo, defined outside of this component, etc.)
      enableRowSelection: true, //enable some features
      enableColumnOrdering: true, //enable a feature for all columns
      enableGlobalFilter: false, //turn off a feature
    });
  
    //note: you can also pass table options as props directly to <MaterialReactTable /> instead of using useMaterialReactTable
    //but the useMaterialReactTable hook will be the most recommended way to define table options
    return <MaterialReactTable table={table} />;
}
 
export default TableView;