import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Button, Layout, Menu, Space, Typography } from 'antd';
import {
    HomeOutlined,
    PlusCircleOutlined,
    LogoutOutlined,
    LoginOutlined,
    UserAddOutlined
} from '@ant-design/icons';

const { Header } = Layout;
const { Title } = Typography;

const Navbar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    const menuItems = [
        {
            key: 'home',
            icon: <HomeOutlined />,
            label: <Link to="/">Home</Link>,
        },
        {
            key: 'create',
            icon: <PlusCircleOutlined />,
            label: <Link to="/create-challenge">Create Challenge</Link>,
        }
    ];

    const authButtons = user ? (
        <Space>
            <Button type="text" icon={<LogoutOutlined />} onClick={handleLogout}>
                Logout
            </Button>
        </Space>
    ) : (
        <Space>
            <Button type="primary" icon={<LoginOutlined />} onClick={() => navigate('/login')}>
                Login
            </Button>
            <Button icon={<UserAddOutlined />} onClick={() => navigate('/register')}>
                Register
            </Button>
        </Space>
    );

    return (
        <Header style={{
            background: '#fff',
            padding: '0 24px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            position: 'sticky',
            top: 0,
            zIndex: 1000,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
        }}>
            <div style={{ display: 'flex', alignItems: 'center' }}>
                <Title level={3} style={{ margin: 0, marginRight: '24px' }}>
                    <Link to="/" style={{ color: '#1890ff' }}>Locle</Link>
                </Title>
                {user && (
                    <Menu
                        mode="horizontal"
                        items={menuItems}
                        style={{ border: 'none', lineHeight: '64px' }}
                    />
                )}
            </div>
            {authButtons}
        </Header>
    );
};

export default Navbar; 