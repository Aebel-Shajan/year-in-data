import { useState } from "react";
import Heatmap from "./components/Heatmap/Heatmap";
import Navbar from "./components/Navbar";
import ModalButton from "./components/ModalButton";
import { axiosInstance } from "./api/axiosClient";

const HeatmapContainer = (
  {
    children
  }: {
    children: React.ReactNode
  }
) => {
  return <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-fit max-w-full">
    {children}
  </div>
}

const HomePage = () => {
  const [authStatus, setAuthStatus] = useState(false)
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [year, setYear] = useState(2023)

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async (url: string) => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axiosInstance.post(
        url,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      if (response.status == 201) {
        alert("File uploaded successfully!");
        setFile(null);
      } else {
        alert("Failed to upload file.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file.");
    } finally {
      setUploading(false);
    }
  };

  async function handleSyncGithub(url: string) {
    try {
      const response = await axiosInstance.post(url)
      if (response.status == 201) {
        alert(`Successfully synced github data for ${url}`);
      } else {
        alert("Failed to sync!");
      }
    } catch (error) {
      console.error("Error syncing", error)
      alert("Error syncing github data.")
    }
  }


  return (
    <div className="min-h-screen bg-base-200 max-w-screen overflow-x-hidden">
      <Navbar
        authStatus={authStatus}
        setAuthStatus={setAuthStatus}
        year={year}
        setYear={setYear}
      />

      <div className="p-8 min-h-screen w-full flex flex-col items-center gap-5">
        <HeatmapContainer>

          <div className="flex justify-between">

            <h1 className="text-xl font-semibold">
              Reading Activity
            </h1>
            <ModalButton buttonText="upload files" >
              <div className="flex flex-col gap-5">

                <h1 className="font-semibold text-xl">Upload kindle zip</h1>
                <input
                  type="file"
                  className="file-input"
                  accept=".zip"
                  onChange={handleFileChange}
                />
                {file && <p className="text-sm text-gray-600">Selected: {file.name}</p>}
                <button onClick={() => handleUpload("/reading/upload_file")} disabled={uploading || !file} className="btn w-full">
                  {uploading ? "Uploading..." : "Upload File"}
                </button>
              </div>

            </ModalButton>
          </div>
          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap
              url={"/reading/" + year}
              name="reading"
              year={year}
            />
          </div>
        </HeatmapContainer>

        <HeatmapContainer>

          <div className="flex justify-between">

            <h1 className="text-xl font-semibold">
              Github Activity
            </h1>
            <button className="btn" onClick={() => handleSyncGithub("/github/" + year)}>

              {`Sync ${year} Github activity`}
            </button>

          </div>
          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap
              url={"/github/" + year}
              name="github"
              year={year}
            />
          </div>
        </HeatmapContainer>


        <HeatmapContainer>

          <div className="flex justify-between" >
            <h1 className="text-xl font-semibold">
              Workout Activity
            </h1>
            <ModalButton buttonText="upload files" >
              <div className="flex flex-col gap-5">

                <h1 className="font-semibold text-xl">Upload strong csv files</h1>
                <input
                  type="file"
                  className="file-input"
                  accept=".csv"
                  onChange={handleFileChange}
                />
                {file && <p className="text-sm text-gray-600">Selected: {file.name}</p>}
                <button onClick={() => handleUpload("/workouts/upload_file")} disabled={uploading || !file} className="btn w-full">
                  {uploading ? "Uploading..." : "Upload File"}
                </button>
              </div>

            </ModalButton>
          </div>

          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap
              url={"/workouts/" + year}
              name="workouts"
              year={year}
              colorRange={["powderblue", "slateblue"]}
            />
          </div>
        </HeatmapContainer>


        <HeatmapContainer>
          <div className="flex justify-between">
            <h1 className="text-xl font-semibold">
              Step Activity
            </h1>
            <ModalButton buttonText="upload files">
              <div className="flex flex-col gap-5">

                <h1 className="font-semibold text-xl">Upload fitbit zip file</h1>
                <input
                  type="file"
                  className="file-input"
                  accept=".zip"
                  onChange={handleFileChange}
                />
                {file && <p className="text-sm text-gray-600">Selected: {file.name}</p>}
                <button onClick={() => handleUpload("/fitbit/upload_file")} disabled={uploading || !file} className="btn w-full">
                  {uploading ? "Uploading..." : "Upload File"}
                </button>
              </div>
            </ModalButton>
          </div>

          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap
              url={"/fitbit/steps/" + year}
              name="steps"
              year={year}
            />
          </div>

        </HeatmapContainer>





      </div>

    </div>
  );
};

export default HomePage;
