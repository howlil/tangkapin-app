import React from 'react'
import DashboardLayout from '../components/layouts/DashboardLayout'
import api from '../utils/api'
import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import DetailReportSection from './sections/DetailReportSection'

export default function DetailReport() {
  const { predict_id } = useParams()
  const [data, setData] = useState([])

  useEffect(() => {
    async function fetchData() {
      const { data } = await api.get(`/api/v2/reports/${predict_id}`)
      console.log(data.data)
      setData(data.data)
    }
    fetchData()
  }, [])

  return (
    <DashboardLayout>
      <DetailReportSection data={data}/>
    </DashboardLayout>
  )
}
