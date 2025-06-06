
const Navbar = (
  {
    year,
    setYear
  }:
    {
      year: number,
      setYear: CallableFunction
    }
) => {

  function handleSelectYear(year: number) {
    const elem = document.activeElement as HTMLElement;
    if (elem) {
      elem?.blur();
    }
    setYear(year)
  }
  return (
    <div className="navbar bg-base-100 shadow-sm fixed top-0 z-999">


      <div className="flex items-center w-full gap-3 px-4">
        <div className="dropdown">
          <a tabIndex={0} role="button" className="btn font-semibold">{year}</a>
          <ul tabIndex={0} className="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm">
            {range(2023, new Date().getFullYear()).map((year) => <li key={year}><a onClick={() => handleSelectYear(year)}>{year}</a></li>)}
          </ul>
        </div>

        <div className="font-semibold text-xl">
          Year in data
        </div>

      </div>

    </div>
  );
};


function range(start: number, end: number) {
  const list = [];
  for (let i = start; i <= end; i++) {
    list.push(i);
  }
  return list
}

export default Navbar;