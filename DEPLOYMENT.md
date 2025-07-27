# 🚀 Unified Deployment Guide

The Co-Intelligence GenAI Universe now uses a **single Docker Compose file** that automatically detects whether you're deploying locally or in the cloud based on the `PUBLIC_IP` setting in your `.env` file.

## 🔧 How It Works

The system automatically detects your deployment environment:

- **If `PUBLIC_IP=localhost`** → Local development mode
  - Debug mode enabled
  - Hot reload enabled
  - Development optimizations

- **If `PUBLIC_IP=your_ec2_ip`** → Cloud production mode
  - Debug mode disabled
  - Production optimizations
  - Multiple workers

## 🚀 Quick Start

### For Local Development

1. **Edit `.env` file:**
   ```bash
   nano .env
   
   # Set these values:
   PUBLIC_IP=localhost
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   ```

2. **Deploy:**
   ```bash
   docker-compose up -d --build
   ```

3. **Access:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - AI Chat: http://localhost:8501
   - Document Analysis: http://localhost:8502
   - Web Search: http://localhost:8503

### For Cloud Deployment (EC2)

1. **Edit `.env` file:**
   ```bash
   nano .env
   
   # Set these values:
   PUBLIC_IP=your_ec2_public_ip_here
   AWS_ACCESS_KEY_ID=your_access_key_here
   AWS_SECRET_ACCESS_KEY=your_secret_key_here
   JWT_SECRET_KEY=your-production-secret-key
   POSTGRES_PASSWORD=your-secure-password
   ```

2. **Deploy:**
   ```bash
   docker-compose up -d --build
   ```

3. **Access:**
   - Frontend: http://your_ec2_ip:3000
   - Backend API: http://your_ec2_ip:8000/docs
   - AI Chat: http://your_ec2_ip:8501
   - Document Analysis: http://your_ec2_ip:8502
   - Web Search: http://your_ec2_ip:8503

## 🔄 Switching Between Environments

To switch from local to cloud or vice versa:

1. **Update `.env` file:**
   ```bash
   # For local:
   PUBLIC_IP=localhost
   
   # For cloud:
   PUBLIC_IP=your_ec2_ip
   ```

2. **Redeploy:**
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

## 🛠️ Management Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop everything
docker-compose down

# Rebuild and restart
docker-compose up -d --build
```

## 🔍 Troubleshooting

### Check Environment Detection
```bash
# Check what environment is detected
curl http://localhost:8000/api/v1/config  # Local
curl http://your_ec2_ip:8000/api/v1/config  # Cloud
```

### Verify Apps Configuration
```bash
# Check if apps are loaded correctly
curl http://localhost:8000/api/v1/apps  # Local
curl http://your_ec2_ip:8000/api/v1/apps  # Cloud
```

### Common Issues

1. **"No applications found"**
   - Check if backend is running: `docker-compose ps`
   - Verify PUBLIC_IP in .env matches your access URL
   - Check backend logs: `docker-compose logs backend`

2. **Quick access links go to wrong URL**
   - Verify PUBLIC_IP setting in .env file
   - Rebuild frontend: `docker-compose up -d --build frontend`

3. **AWS/AI features not working**
   - Verify AWS credentials in .env file
   - Check backend logs for AWS errors: `docker-compose logs backend`

## 📋 EC2 Security Group Requirements

For cloud deployment, ensure your EC2 security group allows:
- Port 22 (SSH)
- Port 3000 (Frontend)
- Port 8000 (Backend API)
- Port 8501 (AI Chat)
- Port 8502 (Document Analysis)
- Port 8503 (Web Search)

## ✅ Verification Checklist

After deployment, verify:
- [ ] All services are running: `docker-compose ps`
- [ ] Frontend loads at correct URL
- [ ] Backend API accessible at /docs endpoint
- [ ] Apps list shows in frontend (not "No applications found")
- [ ] Quick access links use correct IP/hostname
- [ ] All three AI apps are accessible
- [ ] Authentication system works (register/login)

---

**That's it!** One `.env` file, one `docker-compose up -d --build` command, works everywhere! 🎉
