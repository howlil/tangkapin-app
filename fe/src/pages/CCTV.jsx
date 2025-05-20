import DashboardLayout from "../components/layouts/DashboardLayout"


export default function CCTV() {
  return (
    <DashboardLayout>
      <div>
        <h3>CCTV Live Stream</h3>
        <iframe
          src="http://192.168.98.181:8080"
          width="45%"
          height="250px"
          style={{ border: "none" }}
          allowFullScreen
          title="CCTV Stream"
        ></iframe>
      </div>
    </DashboardLayout>
  )
}
