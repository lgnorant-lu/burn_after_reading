import axios from 'axios'

// -----------------------------------------------------------------------------
// API 客户端配置
// -----------------------------------------------------------------------------
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001', // API的基础URL
  timeout: 30000, // 请求超时
})

// -----------------------------------------------------------------------------
// 类型定义
// -----------------------------------------------------------------------------

export type ExpirationType = 'read_once' | 'one_hour' | 'one_day' | 'one_week'

export interface CreateNoteRequest {
  expiration_type: ExpirationType
  content?: string
  file?: File
  password?: string
}

export interface CreateNoteResponse {
  note_id: string
  access_url: string
  created_at: string
  expires_at?: string
}

export interface NoteInfoResponse {
  note_type: 'text' | 'file'
  password_protected: boolean
  expires_at?: string | undefined
}

export interface BackendNoteResponse {
  id: string
  content?: string
  filename?: string
  content_type?: string
  file_size?: string
  has_password: boolean
  expiration_type: ExpirationType
  expires_at?: string
  created_at: string
}

export interface AccessNoteResponse {
  content: string
  expiration_type: string
}

// -----------------------------------------------------------------------------
// API 服务
// -----------------------------------------------------------------------------

const apiService = {
  /**
   * 获取笔记的元信息 (非破坏性)
   * @param id 笔记ID
   */
  async getNoteInfo(id: string): Promise<NoteInfoResponse> {
    const response = await apiClient.get<BackendNoteResponse>(`/note/${id}/info`)
    const data = response.data
    
    // 将后端响应映射为前端期望的格式
    return {
      note_type: data.filename ? 'file' : 'text',
      password_protected: data.has_password,
      expires_at: data.expires_at
    }
  },

  /**
   * 创建一个文本笔记
   * @param data 创建请求
   */
  async createNote(data: CreateNoteRequest): Promise<CreateNoteResponse> {
    const response = await apiClient.post<BackendNoteResponse>('/create', data, {
      headers: { 'Content-Type': 'application/json' },
    })
    const backendData = response.data
    
    // 将后端响应映射为前端期望的格式
    const result: CreateNoteResponse = {
      note_id: backendData.id,
      access_url: `${window.location.origin}/note/${backendData.id}`,
      created_at: backendData.created_at,
    }
    if (backendData.expires_at) {
      result.expires_at = backendData.expires_at
    }
    return result
  },

  /**
   * 上传一个文件
   * @param file 要上传的文件
   * @param password 可选的密码
   * @param expiration_type 过期类型
   */
  async uploadFile(
    file: File,
    password: string | undefined,
    expiration_type: ExpirationType
  ): Promise<CreateNoteResponse> {
    const formData = new FormData()
    formData.append('file', file)
    if (password) {
      formData.append('password', password)
    }
    formData.append('expiration_type', expiration_type)

    const response = await apiClient.post<BackendNoteResponse>('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    const backendData = response.data
    
    // 将后端响应映射为前端期望的格式
    const result: CreateNoteResponse = {
      note_id: backendData.id,
      access_url: `${window.location.origin}/note/${backendData.id}`,
      created_at: backendData.created_at,
    }
    if (backendData.expires_at) {
      result.expires_at = backendData.expires_at
    }
    return result
  },

  /**
   * 获取文本笔记内容 (破坏性)
   * @param id 笔记ID
   * @param password 可选的密码
   */
  async getNote(id: string, password?: string): Promise<AccessNoteResponse> {
    const response = await apiClient.post<AccessNoteResponse>(
      `/note/${id}`,
      { password },
      { headers: { 'Content-Type': 'application/json' } }
    )
    return response.data
  },

  /**
   * 下载文件 (破坏性)
   * @param id 笔记ID
   * @param password 可选的密码
   */
  async downloadFile(id: string, password?: string): Promise<Blob> {
    const response = await apiClient.post<Blob>(
      `/note/${id}/download`,
      { password },
      { 
        headers: { 'Content-Type': 'application/json' },
        responseType: 'blob' 
      }
    )
    return response.data
  },

  /**
   * 健康检查
   */
  async healthCheck(): Promise<{ status: string }> {
    const response = await apiClient.get<{ status: string }>('/health')
    return response.data
  },
}

export { apiService } 