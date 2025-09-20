# 🎯 Legal AI Demo Script (3 Minutes)

## 🚀 **System Overview**
**Paper Clarity** - AI-powered legal document analysis with risk assessment and intelligent Q&A

---

## 📋 **Demo Flow (3 Minutes)**

### **1. Introduction (30 seconds)**
- "Welcome to Paper Clarity, an AI-powered legal document analysis platform"
- "I'll show you how it can analyze legal documents, assess risks, and answer questions intelligently"
- "The system processes documents securely and automatically deletes them after 24 hours for privacy"

### **2. Document Upload (45 seconds)**
- Navigate to `http://localhost:3000`
- Click "Select Document" or drag & drop a legal document
- **Demo file**: Upload any PDF/DOCX legal document (contract, lease, terms of service)
- Show the upload progress and validation
- "The system accepts PDF, DOC, and DOCX files up to 10MB"

### **3. Analysis & Risk Assessment (60 seconds)**
- Wait for analysis to complete (shows processing indicator)
- **Risk Dashboard**: Point out the pie chart showing High/Medium/Low risk distribution
- **Risk Score**: Highlight the overall risk score (0-100)
- **Clause Cards**: Show individual clauses with:
  - Color-coded risk levels (red=high, yellow=medium, green=low)
  - Expandable original text
  - AI-generated summaries
  - Copy functionality
- "Each clause is analyzed for legal risk using advanced heuristics"

### **4. AI Chat Interaction (45 seconds)**
- **Ask Questions**: "What are the penalty clauses?"
- Show the AI response with:
  - Natural language answers
  - **References**: Highlight which clauses were used
  - Multiple relevant clauses if applicable
- **Try More Questions**:
  - "What are the termination conditions?"
  - "What are the payment terms?"
  - "What are the confidentiality obligations?"
- Show how references appear below each answer

### **5. Privacy & Security (30 seconds)**
- Point out the disclaimer banners
- "Documents are processed securely and automatically deleted after 24 hours"
- "No data is stored permanently on our servers"
- "This ensures complete privacy for sensitive legal documents"

---

## 🎬 **Key Demo Points to Highlight**

### **✅ Technical Features**
- **Drag & Drop Upload** with file validation
- **Real-time Risk Analysis** with color-coded indicators
- **Semantic Search** for intelligent Q&A
- **Reference Tracking** showing which clauses were used
- **Responsive Design** works on mobile and desktop
- **Dark Mode** support

### **✅ AI Capabilities**
- **Intelligent Risk Classification** using advanced heuristics
- **Natural Language Processing** for document understanding
- **Semantic Search** finds relevant clauses even with different wording
- **Contextual Answers** that reference specific document sections

### **✅ Privacy & Security**
- **Auto-delete** after 24 hours
- **No permanent storage** of sensitive documents
- **Secure processing** with temporary file handling
- **Clear disclaimers** about AI-generated content

---

## 🗣️ **Sample Demo Script**

> "Let me show you Paper Clarity in action. First, I'll upload a legal document - notice the drag-and-drop interface and file validation. The system is now analyzing the document using AI to identify clauses and assess risks.
> 
> Here we can see the risk dashboard with a clear breakdown - 3 high-risk clauses, 2 medium-risk, and 1 low-risk. Each clause card shows the original text, AI summary, and risk level with color coding.
> 
> Now for the intelligent Q&A - I'll ask 'What are the penalty clauses?' and you can see the AI found relevant sections and provided a natural language answer, with clear references to the specific clauses it used.
> 
> The system is designed for privacy - documents are automatically deleted after 24 hours, and all processing is done securely without permanent storage."

---

## 🛠️ **Technical Setup for Demo**

### **Backend (Port 8001)**
```bash
cd backend
py backend/main.py
```

### **Frontend (Port 3000)**
```bash
cd frontend
npm run dev
```

### **Demo URLs**
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8001/docs
- **Health Check**: http://localhost:8001/health

---

## 📊 **Expected Demo Results**

### **Risk Analysis**
- Clear risk distribution visualization
- Accurate risk scoring based on legal keywords
- Color-coded clause cards for easy identification

### **AI Chat**
- Natural language responses
- Accurate clause references
- Semantic understanding of questions
- Fallback to keyword search if needed

### **User Experience**
- Smooth upload and processing
- Responsive design
- Clear error handling
- Professional UI with dark mode

---

## 🎯 **Demo Success Metrics**

- ✅ **Upload works** in under 10 seconds
- ✅ **Analysis completes** in under 30 seconds
- ✅ **Risk assessment** shows meaningful distribution
- ✅ **Chat responses** are relevant and include references
- ✅ **UI is responsive** and professional
- ✅ **Privacy features** are clearly communicated

---

## 🚨 **Troubleshooting**

### **If Backend Fails**
- Check Python dependencies: `py -m pip install fastapi uvicorn sentence-transformers`
- Verify port 8001 is available
- Check console for error messages

### **If Frontend Fails**
- Check Node.js dependencies: `npm install`
- Verify port 3000 is available
- Check browser console for errors

### **If Chat Doesn't Work**
- Verify backend is running on port 8001
- Check API endpoint responses in browser dev tools
- Ensure document has been analyzed first

---

**🎉 Ready to Demo!** The system is production-ready with all features working smoothly.