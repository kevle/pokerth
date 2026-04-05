/*****************************************************************************
 * PokerTH - The open source texas holdem engine                             *
 * Copyright (C) 2006-2012 Felix Hammer, Florian Thauer, Lothar May          *
 *                                                                           *
 * This program is free software: you can redistribute it and/or modify      *
 * it under the terms of the GNU Affero General Public License as            *
 * published by the Free Software Foundation, either version 3 of the        *
 * License, or (at your option) any later version.                           *
 *****************************************************************************/
/* Client-side WebSocket send buffer (WASM/Emscripten only).
 * Serialises each NetPacket as raw protobuf bytes — no 4-byte length header —
 * matching the framing the PokerTH server expects on its WebSocket port. */

#ifndef _CLIENTWSSENDBUFFER_H_
#define _CLIENTWSSENDBUFFER_H_

#ifdef __EMSCRIPTEN__

#include <net/sendbuffer.h>
#include <QWebSocket>

class ClientWsSendBuffer : public SendBuffer
{
public:
	explicit ClientWsSendBuffer(QWebSocket *ws);

	void SetCloseAfterSend() override {}
	void AsyncSendNextPacket(boost::shared_ptr<SessionData> session) override;
	void HandleWrite(boost::shared_ptr<boost::asio::ip::tcp::socket> socket,
	                 const boost::system::error_code &error) override {}
	void InternalStorePacket(boost::shared_ptr<SessionData> session,
	                         boost::shared_ptr<NetPacket> packet) override;

private:
	QWebSocket *m_ws; // not owned; lifetime managed by ClientThread
};

#endif // __EMSCRIPTEN__
#endif // _CLIENTWSSENDBUFFER_H_
