import { useEffect } from "react";
import { axiosInstance, fetchData } from "../api/axiosClient";
import ThemeController from "./ThemeController";

interface AuthStatus {
  is_authenticated: boolean,
  // username: string
}

const Navbar = (
  {
    authStatus,
    setAuthStatus,
    year,
    setYear
  }:
    {
      authStatus: boolean,
      setAuthStatus: CallableFunction,
      year: number,
      setYear: CallableFunction
    }
) => {

  useEffect(() => {
    (async () => {
      const data = await fetchData<AuthStatus>("/github/auth_status")
      const isAuthenticated = Boolean(data['is_authenticated'])
      setAuthStatus(isAuthenticated)
    })();


  }, [])

  function handleGithubLogin() {
    const authUrl = axiosInstance.getUri() + "github/auth"
    window.open(authUrl, '_blank')?.focus()
  }

  function handleSelectYear(year: number) {
    const elem = document.activeElement as HTMLElement;
    if (elem) {
      elem?.blur();
    }
    setYear(year)
  }
  return (
    <div className="navbar bg-base-100 shadow-sm">


      <div className="navbar-start">

        <div className="font-semibold text-xl px-8">
          Year in data
        </div>
        <div className="dropdown">
          <a tabIndex={0} role="button" className="btn m-1 font-semibold text-xl">{year}</a>
          <ul tabIndex={0} className="dropdown-content menu bg-base-100 rounded-box z-1 w-52 p-2 shadow-sm">
            {range(2023, new Date().getFullYear()).map((year) => <li><a onClick={() => handleSelectYear(year)}>{year}</a></li>)}
          </ul>
        </div>

      </div>



      <div className="navbar-end flex-none gap-5">
        <ThemeController />
        {authStatus ?
          <a className="btn">Log out</a>
          : <a className="btn" onClick={handleGithubLogin}>Dev Login</a>
        }

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