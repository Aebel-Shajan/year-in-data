import { useEffect, useState } from "react";
import { axiosInstance, fetchData } from "../dist/api/axiosClient";
import styles from "./ManageData.module.css"
import { FaGithub } from "react-icons/fa6";
import TableView from "./TableView/TableView";


interface auth_status {
  "is_authenticated": string
}


export interface GithubActivity { 
  "id": number
  "date": string
  "repository_image": string
  "repository_name": string
  "repository_url": string
  "total_commits": number
}

interface activity_response {
  "data": GithubActivity[]
}


const ManageData = () => {
  const [authStatus, setAuthStatus] = useState(false)
  const [githubActivity, setGithubActivity] = useState<GithubActivity[]>([])

  useEffect(() => {
    (async () => {
      const data = await fetchData<auth_status>("/github/auth_status")
      const isAuthenticated = Boolean(data['is_authenticated'])
      setAuthStatus(isAuthenticated)


      const activity = await fetchData<activity_response>("/github/2024")
      setGithubActivity(activity["data"])

    })();
    

  }, [])

  function handleGithubLogin() {
    const authUrl = axiosInstance.getUri() + "github/auth"
    window.open(authUrl, '_blank')?.focus()
  }

  if (!authStatus) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.container}>
          <h1>Authenticate with Github</h1>
          <p>
            Authenticate with github first to manage data. (Currently only accessible to devs :P)
          </p>
          <p>  
            Refresh page if you've already logged in.
          </p>
          <button
            className={styles.ghSignInButton}
            onClick={handleGithubLogin}
          >
            <FaGithub />
            Sign in with GitHub
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.pageContainer}>
      <div className={styles}>
        <h1>Manage Data</h1>
        <TableView data={githubActivity} />
      </div>
    </div>
  );
}

export default ManageData;