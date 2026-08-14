      - name: 安装推送报告所需依赖
        run: pip install requests
        
      - name: 发送经济运行日报邮件
        env:
          EMAIL_SENDER: ${{ secrets.EMAIL_SENDER }}
          EMAIL_RECEIVER: ${{ secrets.EMAIL_RECEIVER }}
          EMAIL_PASSWORD: ${{ secrets.EMAIL_PASSWORD }}
        run: python send_report.py