FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY NetDemo.sln .
COPY src/NetDemo/NetDemo.csproj src/NetDemo/
COPY tests/NetDemo.Tests/NetDemo.Tests.csproj tests/NetDemo.Tests/
RUN dotnet restore
COPY . .
RUN dotnet publish NetDemo.sln -c Release -o /app/publish /p:PublishTrimmed=false

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
ARG APP_UID=1000
RUN addgroup --gid $APP_UID app && adduser --disabled-password --gecos "" --uid $APP_UID --gid $APP_UID app
USER app
ENTRYPOINT ["dotnet", "NetDemo.dll"]
